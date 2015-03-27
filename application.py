#coding:utf-8

from urls import urls
from page import *

import tornado.web
import  torndb
import os


SETTINGS = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "./static"),
        cookie_secret = "71oETzKXQAGaYdkL5gEdGeJJFuYh7EQnp2XdTP1o/Vo=",
        login_url = "/login",
        ui_modules={'Paginator': Paginator,'date_format':date_format,'socket_type_format':socket_type_format},
        debug = True
)

application = tornado.web.Application(
                handlers = urls,
                **SETTINGS
                
                
)

