
from tornado.web import authenticated

from ._netflix import Disc, NetflixHandler, consolidate_queue
from .base import route


@route('/titles')
class TitlesHandler(NetflixHandler):

    @authenticated
    def get(self):
        netflix_queue_url = 'catalog/titles/dvd'
        xx = self.netflix_get(netflix_queue_url, max_results=500)
        self.write(xx)


@route('/home')
class HomeHandler(NetflixHandler):

    @authenticated
    def get(self):
        netflix_queue_url = 'users/{userid}/queues/disc'

        xx = self.netflix_get(netflix_queue_url, max_results=500)
        discs = list()
        for d in xx['queue']['queue_item']:
            d_ = Disc.from_d(d)
            discs.append(d_)

        new_q = consolidate_queue(discs)
        # something lame with json encoding meh
        qq = []
        for d in new_q:
            qq.append( dict( id=d.id, boxart=d.boxart, title=d.title ) )

        self.render('home.html', proposed = qq)


