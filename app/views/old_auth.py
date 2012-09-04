import json

import tornado.gen as gen
from tornado.auth import OAuthMixin
from tornado.web import asynchronous, HTTPError

from .base import BaseHandler, route
from ._netflix import NetflixMixin
from ..models import User


@route('/auth/netflix/connect/?')
class Auth(BaseHandler, NetflixMixin):

    @asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            print self.request
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect(
            callback_uri = self.settings['netflix_callback_uri']
            )

    @gen.engine
    def _on_auth(self, user_d):
        if not user_d:
            raise HTTPError(500, "OAuth failed")
        print "USER_D", user_d

        # self.set_current_user(user)

        # self.redirect('/')
