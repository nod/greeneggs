
import json
from os.path import dirname
from unittest import TestCase

import mock

from .. import Kill, User, CheckIn
from ...game import TheGame


class KillTests(TestCase):

    @classmethod
    def setUpClass(cls):

        for u in User.find(): u.delete()
        for c in CheckIn.find(): c.delete()

        ufix = json.load(
            open('{}/user.fixture'.format(dirname(__file__)))
            )
        cls.user = User.from_fs_dict(ufix)
        assert cls.user

        # let's open up the fixture and get that setup
        cls.fixture = json.load(
            open('{}/checkin.fixture'.format(dirname(__file__)))
            )
        cls.ckin = CheckIn.from_fs_checkin(cls.fixture)

        cls.other_fixture = json.load(
            open('{}/other_checkin.fixture'.format(dirname(__file__)))
            )
        cls.other_ckin = CheckIn.from_fs_checkin(cls.other_fixture)

    def test_instance(self):
        # save and get the key
        # k = self.ckin.save()
        assert self.ckin

    def test_hits(self):

        with mock.patch.object(TheGame, 'simple_shot') as ss:
            # misses
            ss.side_effect = lambda *a,**ka: False
            k = Kill.hits(self.ckin, self.other_ckin)
            assert not k

            # hits
            ss.side_effect = lambda *a,**ka: True
            k = Kill.hits(self.ckin, self.other_ckin)
            assert k

            # wanted to test kill_cnt gorp here but for some reason, the mogo
            # model is caching my kill_cnt from earlier.  moving on for now...


