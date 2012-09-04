from tornado.web import authenticated

from ._netflix import Disc, NetflixHandler
from .base import route


@route('/pos')
class PositionHandler(NetflixHandler):
    """
    tell netflix to set the position of a video, one at a time, yo
    """

    @authenticated
    def post(self):
        title_id = self.get_argument('tid')
        position = self.get_argument('pos')

        nn = 'users/{userid}/queues/disc'


        print "got", title_id, position
        self.write('ok')

        self.netflix_get(nn, method='post', title_ref=title_id,
                         position=position)

