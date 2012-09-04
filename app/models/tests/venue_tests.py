
import json
from os.path import dirname
from unittest import TestCase

from .. import Venue


class VenueTests(TestCase):

    @classmethod
    def setUpClass(cls):

        # let's open up the fixture and get that setup
        cls.fixture = json.load(
            open('{}/checkin.fixture'.format(dirname(__file__)))
            )
        cls.venue = Venue.from_fs_checkin(cls.fixture)

    def test_instance(self):
        # save and get the key
        # k = self.ckin.save()
        assert self.venue.fsid == self.fixture['venue']['id']
        assert self.venue.name == self.fixture['venue']['name']
        for k in ('city', 'state', 'lat', 'lng'):
            ov = getattr(self.venue, k)
            assert ov == self.fixture['venue']['location'][k]

