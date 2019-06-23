"""JAMPP Url Shorten Restful API - EXTENSIONS"""

from logging import FileHandler, WARNING
from flask import Flask, request, abort, url_for, g, jsonify, redirect
from flask_limiter import Limiter
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_limiter.util import get_remote_address

# constant values
DBFILE = "./pythonsqlite.db"
APIKEY = 'ABCDEF123456789'
RATE_LIMIT = "10/hour"
API_VERSION = 'v1.0'

# initialization
APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DBFILE
APP.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
if not APP.debug:
    FILE_HANDLER = FileHandler('errorLog.txt')
    FILE_HANDLER.setLevel(WARNING)
    APP.logger.addHandler(FILE_HANDLER)
DB = SQLAlchemy(APP)
AUTH = HTTPBasicAuth()
LIMITER = Limiter(
    APP,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)
SHARED_LIMITER = LIMITER.shared_limit(RATE_LIMIT, scope="JAMPP")