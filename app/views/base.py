import socket

from tornado.web import RequestHandler
from tornado.util import ObjectDict

from tornroutes import route

from ..models import User


class BaseHandler(RequestHandler):
    """
    """

    def prepare(self):
        self.settings_ = ObjectDict(self.settings)

    def set_current_user(self, u):
        self.set_secure_cookie(
            'authed_user',
            str(u._id),
            expires_days=7
            )
        self._current_user = u

    def get_current_user(self):

        # short circuit the session gorp
        uid = self.get_secure_cookie('authed_user')
        if not uid: return None
        return User.grab(uid)

    def _handle_request_exception(self, e):
        RequestHandler._handle_request_exception(self,e)
        if self.settings.get('debug_pdb') and not isinstance(e, socket.error):
            import pdb
            pdb.post_mortem()

    def write_error(self, status_code, **kwargs):
        print "ERROR", status_code, kwargs
        self.render('error.html', errstr=str(kwargs))
