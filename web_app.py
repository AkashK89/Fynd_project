#!/usr/bin/env python
import os.path
import sys
from twisted.application import service, internet
from twisted.python import log
from twisted.internet import reactor, task, defer
import cyclone.escape
import cyclone.web
import tornado.web
from web_utils import *
from common import *
from admin import *
from auth import *
from users import *
from movies import *
import getpass

class WebApplication(cyclone.web.Application):
    def __init__(self, app):

        handlers = [
            (r"/api/user", AddUserHandler),
            (r"/api/auth", LoginHandler),
            (r"/api/admin", AddAdminHandler),
            (r"/api/movies", AddMovieHandler),
            (r"/api/movie_list", MovieListHandler),
            (r"/(.*)", cyclone.web.StaticFileHandler, {"path": "static"}),
        ]
        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/static/login.html",
            template_path=os.path.join(os.path.dirname(__file__), "static"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #ToDo: This has to be enabled for production system. Currently
            #disabling it as it is creating issue with REST Clients
            #xsrf_cookies=True,
            xsrf_cookies=False,
            autoescape=None,
        )

        cyclone.web.Application.__init__(self, handlers, **settings)

application = service.Application("GoFynd Project")

webapp = WebApplication(application)
server = internet.TCPServer(8888, webapp, interface="0.0.0.0")
server.setServiceParent(application)
