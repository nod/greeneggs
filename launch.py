#!/usr/bin/env python
from sys import stderr

from mogo import connect as mogo_connect
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.util import ObjectDict


from app.views import routes

def start_instance(settings):
    settings = ObjectDict(settings)
    print >>stderr, "starting server on http://{}:{}".format(
            settings.httpd_address,
            settings.httpd_port,
            )
    http_server = HTTPServer( Application(routes, **settings) )
    http_server.listen(
        settings.httpd_port,
        address=settings.httpd_address
        )
    mogo_connect(settings.dbname, host=settings.dbhost, port=settings.dbport)

    try: IOLoop.instance().start()
    except KeyboardInterrupt: pass


if __name__ == '__main__':
    from settings import settings
    start_instance(settings)

