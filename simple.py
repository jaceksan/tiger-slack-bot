#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

from flask import Flask

# Initialize a Flask app to host the events adapter
app = Flask(__name__)


@app.route("/")
def index():
    return "Hello this is the new version!"
