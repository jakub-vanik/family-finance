#!/usr/bin/python3

import datetime
import flask

def create_periods():
  current_period = flask.g.database.get_current_period()
  if not current_period:
    flask.g.database.insert_period(datetime.datetime(2019, 10, 1))
    current_period = flask.g.database.get_current_period()
  start_date = datetime.datetime.strptime(current_period["start_date"], "%Y-%m-%d %H:%M:%S")
  end_date = datetime.datetime.today().replace(day = 1)
  if start_date < end_date:
    year = start_date.year
    month = start_date.month
    while year != end_date.year or month != end_date.month:
      if month < 12:
        month += 1
      else:
        year += 1
        month = 1
      flask.g.database.insert_period(datetime.datetime(year, month, 1))

def update_differences(period):
  totals = calculate_totals(period)
  for person in flask.g.database.list_persons():
    calculation = calculate(person, period, totals)
    flask.g.database.set_difference(person["id"], period["id"], calculation["difference"])

def calculate_totals(period):
  result = {}
  result["statements"] = flask.g.database.get_statements_sum(period["id"])
  result["incomes"] = flask.g.database.get_incomes_sum(period["id"])
  result["exclusions"] = flask.g.database.get_exclusions_sum(period["id"])
  result["repayments"] = flask.g.database.get_repayments_sum(period["id"])
  next_period = flask.g.database.get_next_period(period["id"])
  if next_period:
    result["statements_next"] = flask.g.database.get_statements_sum(next_period["id"])
    result["expenses"] = result["statements"] + result["incomes"] + result["exclusions"] + result["repayments"] - result["statements_next"]
  else:
    result["statements_next"] = None
    result["expenses"] = None
  return result

def calculate(person, period, totals = None):
  result = {}
  result["statements"] = flask.g.database.get_person_statements_sum(person["id"], period["id"])
  result["incomes"] = flask.g.database.get_person_incomes_sum(person["id"], period["id"])
  result["exclusions"] = flask.g.database.get_person_exclusions_sum(person["id"], period["id"])
  result["repayments"] = flask.g.database.get_person_repayments_sum(person["id"], period["id"])
  next_period = flask.g.database.get_next_period(period["id"])
  if next_period:
    result["statements_next"] = flask.g.database.get_person_statements_sum(person["id"], next_period["id"])
    result["expenses"] = result["statements"] + result["incomes"] + result["exclusions"] + result["repayments"] - result["statements_next"]
  else:
    result["statements_next"] = None
    result["expenses"] = None
  if totals and result["expenses"] and totals["expenses"] and totals["incomes"]:
    result["fair_expenses"] = totals["expenses"] / totals["incomes"] * result["incomes"]
    result["difference"] = result["expenses"] - result["fair_expenses"] - result["repayments"]
  else:
    result["fair_expenses"] = None
    result["difference"] = None
  return result
