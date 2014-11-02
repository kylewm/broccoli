from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(256))
    username = db.Column(db.String(64))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.domain


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship(User, backref='posts')
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    permalink = db.Column(db.String(512))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.relationship(Post, backref='comments')
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))

    # reply, repost, like, mention, etc.
    type = db.Column(db.String(32))
    # source url delivered in the webmention
    source = db.Column(db.String(512))
    # discovered post permalink
    permalink = db.Column(db.String(512))

    received = db.Column(db.DateTime)
    published = db.Column(db.DateTime)

    author_name = db.Column(db.String(128))
    author_url = db.Column(db.String(512))
    author_image = db.Column(db.String(512))

    title = db.Column(db.String(512))
    content = db.Column(db.Text)
    rsvp = db.Column(db.String(32))
