
import json
from os.path import dirname
from unittest import TestCase

from .. import CheckIn, User


class CheckInTests(TestCase):

    @classmethod
    def setUpClass(cls):

        ufix = json.load(
            open('{}/user.fixture'.format(dirname(__file__)))
            )
        User.from_fs_dict(ufix)

        # let's open up the fixture and get that setup
        cls.fixture = json.load(
            open('{}/checkin.fixture'.format(dirname(__file__)))
            )

    def setUp(self):
        self.ckin = CheckIn.from_fs_checkin(self.fixture)

    def test_instance(self):
        # save and get the key
        # k = self.ckin.save()
        assert self.ckin



