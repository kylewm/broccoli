from flask import Blueprint, render_template, url_for, request, abort,\
    make_response, current_app, jsonify

from ..models import User, Post, Comment
from ..extensions import db

import bs4
import datetime
import mf2py
import mf2util
import requests
import urllib


wmrecv = Blueprint('wmrecv', __name__)


def url_matches_domain(target, domain):
    """Make sure that the target URL actually belongs to the user being
    notified
    """
    parsed = urllib.parse.urlparse(target)
    return parsed and '/'.join((parsed.netloc, parsed.path)).startswith(domain)


def find_link_to_target(source_url, source_response, target_urls):
    if source_response.status_code // 2 != 100:
        current_app.logger.warn(
            "Received unexpected response from webmention source: %s",
            source_response.text)
        return None

    # Don't worry about Microformats for now; just see if there is a
    # link anywhere that points back to the target
    soup = bs4.BeautifulSoup(source_response.text)
    for link in soup.find_all(['a', 'link']):
        link_target = link.get('href')
        if link_target in target_urls:
            return link


@wmrecv.route('/<username>/webmention', methods=['POST'])
def webmention(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    source = request.form.get('source')
    if not source:
        return make_response('No source parameter', 400)

    target = request.form.get('target')
    if not target:
        return make_response('No target parameter', 400)

    if not url_matches_domain(target, user.domain):
        return make_response(
            '{} is not a child of user domain {}'.format(target, user.domain),
            400)

    target_resp = requests.get(target)
    if target_resp.status_code // 100 != 2:
        return make_response('Target does not exist', 400)
    canonical_target_url = target_resp.url
    alternate_target_urls = (target, canonical_target_url)

    # check whether the source links to the target or possibly the url
    # that target redirects to
    source_resp = requests.get(source)
    link_to_target = find_link_to_target(source, source_resp,
                                         alternate_target_urls)
    if not link_to_target:
        current_app.logger.warn(
            'Webmention source %s does not appear to link to target %s.',
            source, target)
        return make_response(
            'Could not find any links from source to target', 400)

    # get or create a Post based on the canonical target URL
    post = Post.query.filter_by(
        user=user, permalink=canonical_target_url).first()
    if not post:
        post = Post()
        post.user = user
        post.permalink = canonical_target_url
        db.session.add(post)

    # user owns the target, and source links to the target.
    interp = mf2util.interpret_comment(
        mf2py.Parser(url=source, doc=source_resp.text).to_dict(),
        source, alternate_target_urls)

    comment = Comment.query.filter_by(post=post, source=source).first()
    if not comment:
        comment = Comment()
        comment.post = post
        comment.recieved = datetime.datetime.now()
        db.session.add(comment)

    comment.source = source
    comment.permalink = interp.get('url')
    comment.published = interp.get('published')
    comment.author_name = interp.get('author', {}).get('name')
    comment.author_image = interp.get('author', {}).get('image')
    comment.author_url = interp.get('author', {}).get('url')
    comment.title = interp.get('name')
    comment.content = interp.get('content')
    comment.rsvp = interp.get('rsvp')

    for known_type in ('reply', 'repost', 'like', 'rsvp'):
        if known_type in interp.get('comment_type', []):
            comment.type = known_type
            break
    else:
        comment.type = 'mention'

    db.session.commit()

    return 'Successfully received {} on {}'.format(
        comment.type, post.permalink)
