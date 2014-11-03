import os


class DefaultConfig:
    PROJECT = 'broccoli'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super secret key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:////home/kmahan/projects/broccoli/db.sqlite')
