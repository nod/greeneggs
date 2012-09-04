import re

from datetime import datetime
from random import random


from netflix import NetflixAPI
from .base import BaseHandler as RequestHandler
from tornado.util import ObjectDict


season_re = re.compile(r'^(.+)Season (\d+): Disc (\d+)$')


class Disc(ObjectDict):

    @classmethod
    def season_tag(cls, title):
        return bool( season_re.findall(title) )

    @classmethod
    def from_d(cls, blob):
        t_ = blob['title']['regular']
        d = Disc()
        d.title = t_
        d.boxart = blob['box_art']['small']
        d.category = blob['category']
        d.release_year = blob['release_year']
        d.position = blob.get('position', None)
        d.id = blob['id']
        d.series = Disc.season_tag(t_)
        return d


def consolidate_queue(discs):

    q = dict()
    series = dict()

    for d in discs:

        # we only want discs that are available now.  Just ignore all others
        n_ = (1 for x in d.category if x.get('content','') == "Available Now")
        if not any(n_):
            continue

        d.sort_key = random() + (datetime.now().year - d.release_year)

        # first, is it a series? save those separately momentarily
        if d.series:
            parts = season_re.findall(d.title)
            t, season, disc = parts[0]
            season_tag = '{}.{}'.format(
                    str(season).zfill(3),
                    str(disc).zfill(3)
                    )
            if t not in series:
                d.seasons = dict()
                series[t] = d
            series[t].seasons[season_tag] = d
        else:
            q[d.title] = d


    # now add the most recent disc back for our series
    for t,d in series.iteritems():
        lowest_disc = min( d.seasons.keys() )
        series_disc = d.seasons[lowest_disc]
        q[series_disc.title] = series_disc
        del d.seasons[lowest_disc]

    # create our sorted list
    new_q = sorted( q.values(), key=lambda x:x.sort_key)

    # now add other series back to the queue
    for t,d in series.iteritems():
        for k in sorted(d.seasons.keys()):
            new_q.append( d.seasons[k] )

    return new_q


class NetflixHandler(RequestHandler):

    _nflix = None

    def netflix_api(
            self,
            oauth_token = None,
            oauth_token_secret = None
            ):

        self.require_setting('netflix_consumer_key')
        self.require_setting('netflix_consumer_secret')
        self.require_setting('netflix_callback_uri')

        if not self._nflix or any( (oauth_token, oauth_token_secret) ):
            # (re)create _nflix if it doesn't exist or we get handed a token
            self._nflix = NetflixAPI(
                api_key=self.settings['netflix_consumer_key'],
                api_secret=self.settings['netflix_consumer_secret'],
                oauth_token=oauth_token,
                oauth_token_secret=oauth_token_secret,
                callback_url = self.settings['netflix_callback_uri'],
                )
        return self._nflix


    def netflix_get(self, endpoint, user = None, method='get', **params):
        if not user: user = self.current_user

        if user:
            endpoint = endpoint.format(userid = user.netflix_user_id)

        netflix_api = self.netflix_api(
                oauth_token = user.netflix_oauth_token,
                oauth_token_secret = user.netflix_oauth_token_secret
                )

        m = getattr(netflix_api, method)

        return m(endpoint, params = params)



