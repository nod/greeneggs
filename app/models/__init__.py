
import time
from datetime import datetime, timedelta
from uuid import uuid1

from mogo import Model, Field, ReferenceField
from tornado.util import ObjectDict


class BaseModel(Model):
    pass


class User(BaseModel):
    fname = Field()
    lname = Field()
    netflix_oauth_token = Field()
    netflix_oauth_token_secret = Field()
    netflix_user_id = Field()



