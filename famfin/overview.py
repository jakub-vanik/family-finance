#!/usr/bin/python3

import datetime
import flask

from . import calculator
from . import database

bp = flask.Blueprint("overview", __name__)

def choose_period():
  period_id = int(flask.request.args.get("period", 0))
  if period_id > 0:
    return flask.g.database.get_period(period_id)
  return flask.g.database.get_current_period()

def list_persons(period, totals):
  persons = list(map(lambda p: dict(p), flask.g.database.list_persons()))
  for person in persons:
    person["calculation"] = calculator.calculate(person, period, totals)
    person["differences"] = flask.g.database.get_person_differences_sum(person["id"], period["id"])
  return persons

def format_period(period):
  return datetime.datetime.strptime(period["start_date"], "%Y-%m-%d %H:%M:%S").strftime("%m / %Y")

@bp.route("/")
def index():
  with database.Database() as flask.g.database:
    calculator.create_periods()
    period = choose_period()
    totals = calculator.calculate_totals(period)
    persons = list_persons(period, totals)
    context = {
      "period": period,
      "totals": totals,
      "persons": persons,
      "list_accounts": flask.g.database.list_accounts,
      "list_contracts": flask.g.database.list_contracts,
      "list_periods": flask.g.database.list_periods,
      "get_statement": flask.g.database.get_statement,
      "get_income": flask.g.database.get_income,
      "list_exclusions": flask.g.database.list_exclusions,
      "list_repayments": flask.g.database.list_repayments,
      "format_period": format_period
    }
    return flask.render_template("overview.html", **context)

@bp.route("/set_statement", methods=["POST"])
def set_statement():
  with database.Database() as flask.g.database:
    account_id = int(flask.request.form["account_id"])
    period_id = int(flask.request.form["period_id"])
    opening_balance = float(flask.request.form["opening_balance"])
    flask.g.database.set_statement(account_id, period_id, opening_balance)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    prev_period = flask.g.database.get_prev_period(period_id)
    if prev_period:
      calculator.update_differences(prev_period)
    return flask.redirect(flask.url_for(".index", period = period_id))

@bp.route("/delete_statement", methods=["POST"])
def delete_statement():
  with database.Database() as flask.g.database:
    account_id = int(flask.request.form["account_id"])
    period_id = int(flask.request.form["period_id"])
    flask.g.database.delete_statement(account_id, period_id)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    prev_period = flask.g.database.get_prev_period(period_id)
    if prev_period:
      calculator.update_differences(prev_period)
    return flask.redirect(flask.url_for(".index", period = period_id))

@bp.route("/set_income", methods=["POST"])
def set_income():
  with database.Database() as flask.g.database:
    contract_id = int(flask.request.form["contract_id"])
    period_id = int(flask.request.form["period_id"])
    amount = float(flask.request.form["amount"])
    flask.g.database.set_income(contract_id, period_id, amount)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period_id))

@bp.route("/delete_income", methods=["POST"])
def delete_income():
  with database.Database() as flask.g.database:
    contract_id = int(flask.request.form["contract_id"])
    period_id = int(flask.request.form["period_id"])
    flask.g.database.delete_income(contract_id, period_id)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period_id))

@bp.route("/insert_exclusion", methods=["POST"])
def insert_exclusion():
  with database.Database() as flask.g.database:
    person_id = int(flask.request.form["person_id"])
    period_id = int(flask.request.form["period_id"])
    amount = float(flask.request.form["amount"])
    description = flask.request.form["description"]
    flask.g.database.insert_exclusion(person_id, period_id, amount, description)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period_id))

@bp.route("/update_exclusion", methods=["POST"])
def update_exclusion():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    amount = float(flask.request.form["amount"])
    description = flask.request.form["description"]
    flask.g.database.update_exclusion(id, amount, description)
    exclusion = flask.g.database.get_exclusion(id)
    period = flask.g.database.get_period(exclusion["period_id"])
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period["id"]))

@bp.route("/delete_exclusion", methods=["POST"])
def delete_exclusion():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    exclusion = flask.g.database.get_exclusion(id)
    flask.g.database.delete_exclusion(id)
    period = flask.g.database.get_period(exclusion["period_id"])
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period["id"]))

@bp.route("/insert_repayment", methods=["POST"])
def insert_repayment():
  with database.Database() as flask.g.database:
    person_id = int(flask.request.form["person_id"])
    period_id = int(flask.request.form["period_id"])
    amount = float(flask.request.form["amount"])
    description = flask.request.form["description"]
    flask.g.database.insert_repayment(person_id, period_id, amount, description)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period_id))

@bp.route("/update_repayment", methods=["POST"])
def update_repayment():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    amount = float(flask.request.form["amount"])
    description = flask.request.form["description"]
    flask.g.database.update_repayment(id, amount, description)
    repayment = flask.g.database.get_repayment(id)
    period = flask.g.database.get_period(repayment["period_id"])
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period["id"]))

@bp.route("/delete_repayment", methods=["POST"])
def delete_repayment():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    repayment = flask.g.database.get_exclusion(id)
    flask.g.database.delete_repayment(id)
    period = flask.g.database.get_period(repayment["period_id"])
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", period = period["id"]))
