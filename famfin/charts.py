#!/usr/bin/python3

import datetime
import flask
import json

from . import calculator
from . import database

bp = flask.Blueprint("charts", __name__, url_prefix = "/charts")

def format_period(period):
  return datetime.datetime.strptime(period["start_date"], "%Y-%m-%d %H:%M:%S").strftime("%m / %Y")

def calculate(start, end, field):
  persons = flask.g.database.list_persons()
  periods = flask.g.database.list_periods()[start:end]
  data = []
  data += [["Osoba"] + [x["name"] for x in persons] + [{"role": "annotation"}]]
  data += [[format_period(y)] + [calculator.calculate(x, y)[field] for x in persons] + [""] for y in periods]
  return data

@bp.route("/")
def index():
  with database.Database() as flask.g.database:
    start = int(flask.request.args.get("start", 0))
    end = int(flask.request.args.get("end", len(flask.g.database.list_periods())))
    context = {
      "start": start,
      "end": end,
      "statements": json.dumps(calculate(start, end, "statements")),
      "incomes": json.dumps(calculate(start, end, "incomes")),
      "expenses": json.dumps(calculate(start, end, "expenses")),
      "list_periods": flask.g.database.list_periods,
      "format_period": format_period
    }
    return flask.render_template("charts.html", **context)
