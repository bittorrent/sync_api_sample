#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import posixpath
from flask import Flask, redirect, url_for, render_template, jsonify, abort, request
from sync_api_sample.helper import check_peer_status

app = Flask(__name__)
app.config.from_object('sync_api_sample.config')

@app.route('/', methods=['GET'])
def get_status():
    try:
        data = check_peer_status()
        return render_template("index.html", data=data)
    except:
        abort(500)
