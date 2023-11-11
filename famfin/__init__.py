#!/usr/bin/python3

import flask
import os

from . import backup
from . import charts
from . import overview
from . import setup
from . import upload

class ReverseProxied:

  def __init__(self, app, script_name):
    self.app = app
    self.script_name = script_name

  def __call__(self, environ, start_response):
    environ["SCRIPT_NAME"] = self.script_name
    return self.app(environ, start_response)

def create_app():
  app = flask.Flask(__name__)
  app.register_blueprint(overview.bp)
  app.register_blueprint(charts.bp)
  app.register_blueprint(upload.bp)
  app.register_blueprint(setup.bp)
  app.register_blueprint(backup.bp)
  app.wsgi_app = ReverseProxied(app.wsgi_app, os.environ["SCRIPT_NAME"])
  return app
