
import json
from os.path import dirname
from unittest import TestCase

from .. import User


class UserTests(TestCase):

    def setUp(self):
        # slow
        for u in User.find():
            u.delete()

    def test_instance(self):
        u = User(fname='joe')
        assert u
        # save and get the key
        k = u.save()
        assert k
        # retrieve by key
        u_ = User.grab(k)
        assert u._id == u_.id

        u_ = User.find_one(dict(fname='joe'))
        print u._id
        print u_._id
        assert u._id == u_._id


    def test_from_fs_dict(self):
        u_ = json.load(open('{}/user.fixture'.format(dirname(__file__))))
        u = User.from_fs_dict(u_)
        assert u.fname == u_['firstName']
        assert all((u.fname, u.lname, u.fsid, u.pic, u.acctok))
