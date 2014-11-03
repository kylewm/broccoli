from flask import Blueprint, url_for, redirect, request, abort,\
  render_template, make_response
from ..extensions import db
from ..models import User, Post, Comment


embed = Blueprint('embed', __name__)


@embed.route('/broccoli.js')
def script():
    response = make_response(
        render_template('embed/broccoli.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response



@embed.route('/comments')
def comments():
    """Render comments for a particular post"""
    username = request.args.get('user')
    post_url = request.args.get('post')

    user = User.query.filter_by(username=username).first()
    post = Post.query.filter_by(
        permalink=post_url, user=user).first()

    if not post:
        post = Post()
        post.user = user
        post.permalink = post_url

    return render_template('embed/comments.html', post=post)
