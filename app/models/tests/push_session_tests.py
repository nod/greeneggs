
import json
from datetime import datetime
from os.path import dirname
from unittest import TestCase

import mock

from .. import Kill, User, CheckIn, PushSession


class KillTests(TestCase):

    @classmethod
    def setUpClass(cls):

        for u in User.find(): u.delete()
        for c in CheckIn.find(): c.delete()
        for p in PushSession.find(): p.delete()

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


    def test_push_session(self):
        p = PushSession.create(user=self.user, checkin=self.ckin)
        pid = p._id
        tok = p.token
        assert tok
        assert p.expires > datetime.now()

        # should return a valid user and checkin
        user = PushSession.for_token(p.token)
        assert isinstance(user, User)

        # the checkin should be attached to user for convenience
        assert isinstance(user.session_checkin, CheckIn)

        # should have been deleted by for_token call
        assert not PushSession.find_one(dict(token=tok))
        assert not PushSession.grab(pid)


