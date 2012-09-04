
from .base import BaseHandler, route
from ._foursquare import FoursquareMixin


@route('/auth/fs/?')
class AuthFoursquare(BaseHandler, FoursquareMixin):

    @asynchronous
    def get(self):
        if not self.get_argument("oauth_token", False):
            cb_uri = self.application.settings.get('fs_callback_uri')
            return self.authorize_redirect(callback_uri = cb_uri)
        self.get_authenticated_user(self._on_auth)

    def _on_auth(self, user_d):
        if not user_d:
            raise HTTPError(500, "Foursquare auth failed")
        self.set_current_user(user_d)
        self.redirect('/')

