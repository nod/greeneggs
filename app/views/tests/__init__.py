
import json
import urllib
from os.path import dirname

from tornado.httputil import url_concat
from tornado.testing import AsyncHTTPTestCase
from tornado.util import ObjectDict
from tornado.web import Application, RequestHandler, URLSpec
from tornroutes import route

from .mpatch import CapturePatch, Patch
from ..base import BaseHandler
from ... import settings
from ...models import User


# setup our database for tests
from mogo import connect as mogo_connect
mogo_connect('bastille_test')

settings = ObjectDict(settings)
# fake our foursquare push gorp
settings.fs_push_secret = 'yourmomma'

# i hate having a global var to capture the state of a monkey patched method but
# as long as tests are run serially, this should work well.
_render_state = {}
def patch_render(handler, template_name, **kwargs):
    global _render_state
    assert(not kwargs.has_key('template_name'))
    assert(not kwargs.has_key('current_user'))
    assert(not kwargs.has_key('final_request_uri'))
    assert(not kwargs.has_key('html_body'))
    kwargs['html_body'] = handler.render_string(template_name, **kwargs)
    kwargs['template_name'] = template_name
    kwargs['current_user'] = handler.current_user
    kwargs['final_request_uri'] = handler.request.uri
    _render_state = kwargs
    handler.finish()

class RequestHandlerTest(AsyncHTTPTestCase):

    fs_push_secret = settings.fs_push_secret  # faking this
    _app = None  # for caching

    testing_handler = BaseHandler # will be used for patching that handler directly
    _authenticated_as = None #set to a User object to fake auth'd

    def authenticate_as(self, u):
        """
        when performing tests on a requesthandler, setting this to an instance
        of User will shortcircuit the authentication appropriately
        """
        self._authenticated_as = u

    def get_app(self):
        if self._app: return self._app

        settings.base_uri = self.get_url('/').rstrip('/')
        settings.login_url = '/no-login-handler'
        settings.xsrf_cookies = False
        settings.debug = True
        settings.debug_pdb = False
        self._app = Application( route.get_routes(), **settings )

        return self._app

    def fetch_d(self, path, **kwargs):
        global _render_state
        def patch_gcu(handler, aa=self._authenticated_as):
            return aa
        _render_state = {}
        with Patch( RequestHandler, render = patch_render ):
            with Patch(self.testing_handler, get_current_user = patch_gcu):
                response = self.fetch(path, **kwargs)
                response.render_args = ObjectDict(_render_state)
        return response

    def get_d(self, path, **kwargs):
        return self.fetch_d(url_concat(path,kwargs), method='GET')

    def post_d(self, path, **kwargs):
        return self.fetch_d(
                path,
                method='POST',
                body=urllib.urlencode(kwargs) if kwargs else None,
                )

    def _get_current_user(self):
        return self._authenticated_as

