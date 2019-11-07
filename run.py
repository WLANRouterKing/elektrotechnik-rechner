#!/usr/bin/python
# -*- coding: utf-8 -*-
from cryption_server import create_app

app = create_app()
app.app_context().push()

if __name__ == '__main__':
    app.run(host="localhost")
