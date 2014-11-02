
from flask import Blueprint, render_template, request, redirect,\
    make_response, current_app, url_for, flash

from flask.ext.login import login_user, logout_user, login_required,\
    current_user
import urllib
import requests
import re
import bs4

from ..models import User
from ..extensions import db


dash = Blueprint('dash', __name__)


@dash.route('/')
def index():
    return render_template('index.html', current_user=current_user)


@dash.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        if username != current_user.username:
            # check for weird characters
            if not re.match('[a-zA-Z0-9_]+$', username):
                flash('Usernames cannot contain special characters or spaces',
                      'danger')
            # check for duplicates
            elif User.query.filter_by(username=username).count():
                flash('That username has already been claimed.', 'danger')
            else:
                current_user.username = username
                db.session.commit()

        return redirect(url_for('.user_profile'))
    return render_template('profile.html')


@dash.route('/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('.index'))


@dash.route('/login')
def login():
    me = request.args.get('me')
    if not me:
        return render_template('login.html')

    if not me.startswith('http://') and not me.startswith('https://'):
        me = 'http://' + me

    # default authorization url
    auth_url = 'https://indieauth.com/auth'
    resp = requests.get(me)
    if resp.status_code == 200:
        soup = bs4.BeautifulSoup(resp.text)
        link = soup.find('link', {'rel': 'authorization_endpoint'})
        if link:
            user_auth_url = link.get('href')
            if user_auth_url:
                auth_url = user_auth_url

    current_app.logger.debug('Found auth endpoint %s', auth_url)
    state = '{};{}'.format(auth_url, request.args.get('next', ''))
    auth_params = {
        'me': me,
        'client_id': 'http://brcc.li',
        'redirect_uri': url_for('.login_callback', _external=True),
        'state': state,
    }
    return redirect('{}?{}'.format(
        auth_url, urllib.parse.urlencode(auth_params)))


@dash.route('/loginCallback')
def login_callback():
    current_app.logger.debug('callback fields: %s', request.args)

    state = request.args.get('state')
    next_url = state or url_for('index')
    state_split = request.args.get('state', '').split(';', 1)
    if len(state_split) == 2:
        auth_url = state_split[0]
        next_url = state_split[1]
    else:
        auth_url = 'https://indieauth.com/auth'
        next_url = '/'

    code = request.args.get('code')
    client_id = 'http://brcc.li'
    redirect_uri = url_for('.login_callback', _external=True)

    current_app.logger.debug('callback with auth endpoint %s', auth_url)
    response = requests.post(auth_url, data={
        'code': code,
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
    })

    rdata = urllib.parse.parse_qs(response.text)
    if response.status_code != 200:
        flash('Login failed {}: {}'.format(rdata.get('error'),
                                           rdata.get('error_description')),
              'danger')
        return redirect(next_url)

    current_app.logger.debug('verify response %s', response.text)
    if 'me' not in rdata:
        flash('Verify response missing required "me" field {}'.format(
            response.text), 'danger')
        return redirect(next_url)

    me = rdata.get('me')[0]
    parsed = urllib.parse.urlparse(me)
    if parsed.path:
        domain = '/'.join((parsed.netloc, parsed.path))
    else:
        domain = parsed.netloc

    user = User.query.filter_by(domain=domain).first()
    if not user:
        user = create_new_user(domain)

    login_user(user, remember=True)
    flash('Logged in with domain {}'.format(me), 'success')

    return redirect(next_url)


def create_new_user(domain):
    user = User()
    user.domain = domain
    user.username = domain.replace('[/]', '_')
    db.session.add(user)
    db.session.commit()
