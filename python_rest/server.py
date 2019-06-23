"""JAMPP Url Shorten Restful API."""
import sqlite3
from functools import wraps
from short_url import encode_url, decode_url
from flask import Flask, request, abort, url_for, g, jsonify, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jsonpify import jsonify
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

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
DB = SQLAlchemy(APP)
AUTH = HTTPBasicAuth()
LIMITER = Limiter(
    APP,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)
SHARED_LIMITER = LIMITER.shared_limit(RATE_LIMIT, scope="JAMPP")

# useful functions


def require_apikey(view_function):
    """Returns decorated function for API key."""
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        """API key decorator."""
        if request.args.get('apiKey') and request.args.get('apiKey') == APIKEY:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


def get_table_columns_name(query):
    """Returns table columns names for a specific query."""
    aux_str_list = [x[0] for x in query.description]
    return {aux_str_list[i]: i for i in range(0, len(aux_str_list))}


def create_connection(db_file):
    """Returns a connection to a database."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except BaseException:
        print "Database ERROR: %s" % db_file
        exit(1)


def shorten_url(long_url):
    """Returns short url name."""
    conn = create_connection(DBFILE)  # connect to database
    url_id = conn.cursor().execute(
        'SELECT * FROM urls ORDER BY id DESC LIMIT 1').fetchone()
    if url_id is None:
        url_id = 1
    else:
        url_id = url_id[0] + 1
    conn.cursor().execute(
        ''' INSERT OR IGNORE INTO urls (url_long_name, url_short_name, clicks, date_last_click)
        VALUES ('%s', '%s', 1, DATETIME('now')) ''' %
        (long_url, encode_url(url_id)))
    conn.commit()
    short_url = encode_url(conn.cursor().execute(
        'SELECT * FROM urls ORDER BY id DESC LIMIT 1').fetchone()[0])
    conn.close()

    return short_url


def expand_url(short_url):
    """Returns long url name."""
    conn = create_connection(DBFILE)  # connect to database
    long_url = conn.cursor().execute(
        '''SELECT url_long_name FROM urls WHERE id = '%d' ''' %
        decode_url(short_url)).fetchone()[0]
    conn.close()
    return long_url


def get_clicks_url(long_url):
    """Returns clicks quantity of a specific url."""
    conn = create_connection(DBFILE)  # connect to database
    query_fetched = conn.cursor().execute(
        '''SELECT clicks FROM urls WHERE url_long_name = '%s' LIMIT 1''' %
        long_url).fetchone()
    clicks = 0
    if query_fetched is not None:
        clicks = query_fetched[0]
    conn.close()
    return clicks


def add_click_url(view_function):
    """Add clicks quantity of a specific url to the database."""
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        """API key decorator."""
        long_url = request.args.get('longUrl', default=None, type=str)
        if long_url is None:
            long_url = expand_url(
                request.args.get(
                    'shortUrl',
                    default=None,
                    type=str))
        conn = create_connection(DBFILE)  # connect to database
        conn.cursor().execute(
            ''' UPDATE urls
            SET clicks = %d, date_last_click = DATETIME('now')
            WHERE url_long_name = '%s' ''' %
            (get_clicks_url(long_url) + 1, long_url))
        conn.cursor().execute(
            ''' INSERT INTO urls_clicks (url_long_name, date_click)
            VALUES ('%s', DATETIME('now')) ''' %
            (long_url))
        conn.commit()
        conn.close()
        return view_function(*args, **kwargs)
    return decorated_function


@AUTH.verify_password
def verify_password(username, password):
    """Verify user passwords callback function."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class User(DB.Model):
    """User class for login."""
    __tablename__ = 'users'
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(32), index=True)
    password_hash = DB.Column(DB.String(128))

    def hash_password(self, password):
        """Hash user passwords."""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify user passwords."""
        return pwd_context.verify(password, self.password_hash)


# resources
@APP.route('/api/' + API_VERSION + '/users', methods=['POST'])
def new_user():
    """Create new user."""
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username)
    user.hash_password(password)
    DB.session.add(user)
    DB.session.commit()
    return jsonify({'username': user.username}), 201, {
        'Location': url_for('get_user', id=user.id, _external=True)}


@APP.route('/api/' + API_VERSION + '/login', methods=['GET'])
@AUTH.login_required
def login():
    """Login."""
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@APP.route('/api/' + API_VERSION + '/url', methods=['GET'])
@require_apikey
def get_urls():
    """API get()."""
    conn = create_connection(DBFILE)
    query = conn.cursor().execute("SELECT * FROM urls")
    columns = get_table_columns_name(query)
    return jsonify({i[columns['url_long_name']]: i[columns['clicks']] for i in query.fetchall()})


@APP.route('/api/' + API_VERSION + '/url/<short_url>', methods=['GET'])
def get_redirect(short_url):
    """API get_redirect()."""
    return redirect(expand_url(short_url))


@APP.route('/api/' + API_VERSION + '/url/info', methods=['GET'])
@require_apikey
@SHARED_LIMITER
def get_url_info():
    """API get(apiKey, longUrl)."""
    long_url = request.args.get('longUrl', default=None, type=str)
    short_url = shorten_url(long_url)
    clicks = get_clicks_url(long_url)
    return jsonify('''{'longUrl': %s, 'shortUrl' : %s, 'clicks' : %d}''' % (
        long_url, short_url, clicks))


@APP.route('/api/' + API_VERSION + '/url/shorten', methods=['GET'])
@require_apikey
@add_click_url
@SHARED_LIMITER
def get_url_short_name():
    """API get(apiKey, longUrl)."""
    long_url = request.args.get('longUrl', default=None, type=str)
    short_url = shorten_url(long_url)
    return jsonify('''{'shortUrl' : %s}''' % (short_url))


@APP.route('/api/' + API_VERSION + '/url/expand', methods=['GET'])
@require_apikey
@add_click_url
@SHARED_LIMITER
def get_url_long_name():
    """API get(apiKey, shortUrl)."""
    short_url = request.args.get(
        'shortUrl', default=None, type=str)
    long_url = expand_url(short_url)
    return jsonify('''{'longUrl': %s}''' % (long_url))


@APP.route('/api/' + API_VERSION + '/url/clickStats', methods=['GET'])
@require_apikey
@SHARED_LIMITER
def get_urls_click_stats():
    """API get(apiKey, shortUrl, from, to)."""
    short_url = request.args.get('shortUrl', default='None', type=str)
    from_date = request.args.get('from', default='None', type=str)
    to_date = request.args.get('to', default='None', type=str)
    if short_url != 'None':
        long_url = expand_url(short_url)
    conn = create_connection(DBFILE)  # connect to database
    cur = conn.cursor()
    query = None
    if short_url == 'None':
        if from_date == 'None' or to_date == 'None':
            query = cur.execute('''
                    SELECT count(*) AS clicks, url_long_name AS url
                    FROM urls_clicks
                    GROUP BY url_long_name''')
        else:
            query = cur.execute('''
                    SELECT count(*), url_long_name
                    FROM urls_clicks
                    WHERE date_click BETWEEN '%s' AND '%s'
                    GROUP BY url_long_name
                    ''' % (from_date.replace('T', ' ').replace('Z', ''),
                           to_date.replace('T', ' ').replace('Z', '')))
        columns_names = get_table_columns_name(query)
        return {i[columns_names['url']]: i[columns_names['clicks']]
                for i in query.fetchall()}
    else:
        if from_date == 'None' or to_date == 'None':
            query = cur.execute('''
                    SELECT count(*)  FROM urls_clicks
                    LEFT JOIN urls ON urls_clicks.url_long_name = urls.url_long_name
                    WHERE urls.url_short_name = '%s'
                    ORDER BY urls_clicks.date_click DESC''' % (short_url))
        else:
            query = cur.execute('''
                    SELECT count(*)  FROM urls_clicks
                    LEFT JOIN urls ON urls_clicks.url_long_name = urls.url_long_name
                    WHERE urls.url_short_name = '%s'
                    AND urls_clicks.date_click BETWEEN '%s' AND '%s'
                    ORDER BY urls_clicks.date_click DESC
                    ''' % (short_url, from_date.replace('T', ' ').replace('Z', ''),
                           to_date.replace('T', ' ').replace('Z', '')))
        return jsonify('''{'longUrl': %s, 'shortUrl' : %s, 'clicks' : %d}''' % (
            long_url, short_url, query.fetchone()[0]))


@APP.route('/api/' + API_VERSION + '/', methods=['GET'])
@require_apikey
@LIMITER.limit("100/hour")
def hello_world():
    """API example."""
    return 'Hello world!.'

# curl -i -X POST \
#   -H "Content-Type: application/json"
#   -d '{"username":"alejo","password":"python"}' \
#   http://127.0.0.1:5002/users


# curl -u alejo:python -i -X GET \
#   http://127.0.0.1:5002/login
if __name__ == '__main__':
    APP.run(port='5002')
