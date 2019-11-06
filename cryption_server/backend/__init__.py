#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Blueprint

backend = Blueprint('backend', __name__)

from . import views
