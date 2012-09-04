
from os import path
from tornado.util import ObjectDict

settings = ObjectDict(

    # mongodb settings
    dbname = 'mapthisnow',
    dbhost = None,
    dbport = None,

    # httpd server settings
    httpd_address = '127.0.0.1',
    httpd_port = 9988,
    cookie_secret = None, # ya you're gonna have to set this locally

    # file paths
    static_path = path.join(path.dirname(__file__), "static"),
    template_path = path.join(path.dirname(__file__), "app/templates"),
    login_url = '/auth/netflix/connect',

    # debuggery
    debug = False,
    debug_pdb = False,

    netflix_client_secret = None,
    netflix_client_id = None,
    netflix_callback_uri = 'http://127.0.0.1:9988/auth/netflix/connect',
    )

# pull in our local overrides, if any
try:
    from settings_local import settings as settings_local
    settings.update(settings_local)
except ImportError: pass
