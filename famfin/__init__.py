#!/usr/bin/python3

import flask
import werkzeug.middleware.proxy_fix

from . import backup
from . import charts
from . import overview
from . import setup
from . import upload

app = flask.Flask(__name__)
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app, x_prefix=1)
app.register_blueprint(overview.bp)
app.register_blueprint(charts.bp)
app.register_blueprint(upload.bp)
app.register_blueprint(setup.bp)
app.register_blueprint(backup.bp)
