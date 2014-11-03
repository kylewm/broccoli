from flask import Flask
from .config import DefaultConfig
from .extensions import db, login_mgr
from .wmrecv import wmrecv
from .dash import dash
from .models import User
from .embed import embed
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)
    configure_blueprints(app)
    configure_extensions(app)
    return app


def configure_blueprints(app):
    app.register_blueprint(wmrecv)
    app.register_blueprint(dash)
    app.register_blueprint(embed, url_prefix='/embed')


def configure_extensions(app):
    db.init_app(app)
    login_mgr.init_app(app)

    @login_mgr.user_loader
    def load_user(domain):
        return User.query.filter_by(domain=domain).first()

    login_mgr.login_view = 'dash.login'
