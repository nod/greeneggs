
from . import RequestHandlerTest

class GenericTest(RequestHandlerTest):

    def test_index_responds(self):
        r = self.get_d('/')
        assert r.code == 200

    def test_index_render_args(self):
        r = self.get_d('/')
        assert r.render_args.test_ok is True

