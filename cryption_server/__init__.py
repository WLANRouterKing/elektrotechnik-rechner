#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_navigation import Navigation
from logging.handlers import SysLogHandler

app = Flask(__name__, instance_relative_config=True)
my_logger = logging.getLogger('MyLogger')
login_manager = LoginManager()
mail = Mail()
nav = Navigation()


def create_app():
    # Load the default configuration
    app.config.from_object('config')

    # Load the configuration from the instance folder
    app.config.from_pyfile('config.py')

    my_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s || [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    rotating_file_handler = logging.handlers.RotatingFileHandler(filename='/home/lxkennstenich/PycharmProjects/cryption_server/log.debug')
    rotating_file_handler.setFormatter(formatter)
    my_logger.addHandler(rotating_file_handler)

    login_manager.init_app(app)
    login_manager.session_protection = "strong"
    login_manager.refresh_view = "backend.login"
    login_manager.needs_refresh_message = u"To protect your account, please reauthenticate to access this page."
    login_manager.needs_refresh_message_category = "info"

    mail.init_app(app)
    nav.init_app(app)

    from .backend import backend as backend_blueprint
    from .frontend import frontend as frontend_blueprint
    from .api import api as api_blueprint
    app.register_blueprint(backend_blueprint, url_prefix='/backend/')
    app.register_blueprint(frontend_blueprint, url_prefix='/')
    app.register_blueprint(api_blueprint, url_prefix='/api/')

    return app
