#!/usr/bin/python3

import flask

from . import database

bp = flask.Blueprint("setup", __name__, url_prefix = "/setup")

@bp.route("/")
def index():
  with database.Database() as flask.g.database:
    context = {
      "list_persons": flask.g.database.list_persons,
      "list_accounts": flask.g.database.list_accounts,
      "list_contracts": flask.g.database.list_contracts
    }
    return flask.render_template("setup.html", **context)

@bp.route("/insert_person", methods=["POST"])
def insert_person():
  with database.Database() as flask.g.database:
    name = flask.request.form["name"]
    flask.g.database.insert_person(name)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/update_person", methods=["POST"])
def update_person():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    name = flask.request.form["name"]
    flask.g.database.update_person(id, name)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/delete_person", methods=["POST"])
def delete_person():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    flask.g.database.delete_person(id)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/insert_account", methods=["POST"])
def insert_account():
  with database.Database() as flask.g.database:
    person_id = int(flask.request.form["person_id"])
    name = flask.request.form["name"]
    number = flask.request.form["number"]
    active = int(flask.request.form["active"])
    flask.g.database.insert_account(person_id, name, number, active)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/update_account", methods=["POST"])
def update_account():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    name = flask.request.form["name"]
    number = flask.request.form["number"]
    active = int(flask.request.form["active"])
    flask.g.database.update_account(id, name, number, active)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/delete_account", methods=["POST"])
def delete_account():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    flask.g.database.delete_account(id)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/insert_contract", methods=["POST"])
def insert_contract():
  with database.Database() as flask.g.database:
    person_id = int(flask.request.form["person_id"])
    name = flask.request.form["name"]
    number = flask.request.form["number"]
    active = int(flask.request.form["active"])
    flask.g.database.insert_contract(person_id, name, number, active)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/update_contract", methods=["POST"])
def update_contract():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    name = flask.request.form["name"]
    number = flask.request.form["number"]
    active = int(flask.request.form["active"])
    flask.g.database.update_contract(id, name, number, active)
    return flask.redirect(flask.url_for(".index"))

@bp.route("/delete_contract", methods=["POST"])
def delete_contract():
  with database.Database() as flask.g.database:
    id = int(flask.request.form["id"])
    flask.g.database.delete_contract(id)
    return flask.redirect(flask.url_for(".index"))
