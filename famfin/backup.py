#!/usr/bin/python3

import flask

from . import database

bp = flask.Blueprint("backup", __name__, url_prefix = "/backup")

@bp.route("/dump.sql")
def dump():
  def generate():
    with database.Database() as flask.g.database:
      for line in flask.g.database.dump():
        yield line + "\n"
  return flask.Response(flask.stream_with_context(generate()), mimetype = "text/plain")
