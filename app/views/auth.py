import json

import tornado.gen as gen
from tornado.auth import OAuthMixin
from tornado.web import asynchronous, HTTPError


from .base import BaseHandler, route
from ._netflix import NetflixHandler
from ..models import User


@route('/auth/netflix/connect/?')
class Auth(NetflixHandler):

    def get(self):
        n = self.netflix_api()

        oauth_token = self.get_argument('oauth_token', None)
        oauth_verifier = self.get_argument('oauth_verifier',None)
        if not oauth_token and not oauth_verifier:
            # NOT LOGGED IN
            auth_props = n.get_authentication_tokens()

            # we're gonna want this in a sec
            self.set_secure_cookie(
                    'oauth_token_secret',
                    auth_props['oauth_token_secret']
                    )
            self.redirect( auth_props['auth_url'] )
            return

        # after login
        oauth_token_secret = self.get_secure_cookie('oauth_token_secret')

        n = self.netflix_api(
                oauth_token = oauth_token,
                oauth_token_secret = oauth_token_secret
                )

        authorized_tokens = n.get_auth_tokens(oauth_verifier)

        final_oauth_token = authorized_tokens['oauth_token']
        final_oauth_token_secret = authorized_tokens['oauth_token_secret']
        final_user_id = authorized_tokens['user_id']


        user = User.find_one( {'netflix_user_id': final_user_id } )
        if not user:
            # user's first login
            user = User(
                    netflix_oauth_token = final_oauth_token,
                    netflix_oauth_token_secret = final_oauth_token_secret,
                    netflix_user_id = final_user_id,
                    )
            details =  self.netflix_get('users/{}'.format(final_user_id), user)
            dets = details['user']
            user.fname = dets['first_name']
            user.lname = dets['last_name']
            user.save()

        self.set_current_user(user)
        self.redirect('/home')


