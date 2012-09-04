
from .base import BaseHandler, route


@route('/')
class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html', test_ok=True)

