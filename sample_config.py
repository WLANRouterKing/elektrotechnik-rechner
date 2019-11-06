#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

SERVER_NAME = "127.0.0.1"
HOST = "127.0.0.1"
HOST_PROTOCOL = "http://"
SYSTEM_MODE = ""
DEBUG = True  # Turns on debugging features in Flask
MAIL_ADMIN = ""
DATABASE_HOST = ""
DATABASE_NAME = ""
DATABASE_USER = ""
DATABASE_PASSWORD = ''
# os.urandom(128)
SECRET_KEY = os.urandom(128)
# hexadezimaler string 64 Zeichen
SYM_KEY = ""
MAIL_SERVER = ""
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_DEBUG = False
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = ""
