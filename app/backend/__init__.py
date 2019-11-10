#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Blueprint

backend = Blueprint('backend', __name__, template_folder='templates', static_folder="static")

from . import views
