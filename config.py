import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DB_PATH = os.path.join(basedir, 'db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DB_PATH, 'user.db')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zCIKeCX5vsxd9Yl7CmSnbm15Q0ITFa+nl3+E5Nnad7s='
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME') or 'hhp849730_session'
    HH_CLIENT_ID = os.environ.get('HH_CLIENT_ID')
    HH_CLIENT_SECRET = os.environ.get('HH_CLIENT_SECRET')
    SELF_URL_SCHEME = os.environ.get('SELF_URL_SCHEME')
    SELF_URL_HOST = os.environ.get('SELF_URL_HOST')
    SELF_URL_PORT = os.environ.get('SELF_URL_PORT')
    SELF_URL = SELF_URL_SCHEME + '://' + SELF_URL_HOST + ':' + SELF_URL_PORT
    ITEMS_PER_PAGE = 20
