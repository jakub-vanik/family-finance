#!/usr/bin/python3

import base64
import datetime
import flask
import itertools
import pickle
import re
import xml.etree.ElementTree

from . import calculator
from . import database

bp = flask.Blueprint("upload", __name__, url_prefix = "/upload")

def convert_iban(iban):
  match = re.match("^CZ[0-9]{2}([0-9]{4})([0-9]{16})$", iban)
  return match.group(2).lstrip("0") + "/" + match.group(1)

def parse_date(text):
  return datetime.datetime.strptime(text[0:10], "%Y-%m-%d")

def read_amount(element, namespace):
  value = float(element.find("./x:Amt", namespace).text)
  direction = element.find("./x:CdtDbtInd", namespace).text
  if direction == "CRDT":
    return value
  if direction == "DBIT":
    return -value
  raise Exception("Unknown amount")

def add_balance(balances, date, balance, next_date):
  while date < next_date:
    balances[date] = balance
    date += datetime.timedelta(days = 1)

def process_statement_camt(root):
  statement = {"account": None, "balances": {}, "incomes": []}
  namespace = {"x": re.match("\{(.*)\}", root.tag).group(1)}
  iban = root.find("./x:BkToCstmrStmt/x:Stmt/x:Acct/x:Id/x:IBAN", namespace).text
  statement["account"] = convert_iban(iban)
  bal_entries = root.findall("./x:BkToCstmrStmt/x:Stmt/x:Bal", namespace)
  for bal_entry in bal_entries:
    if bal_entry.find("./x:Tp/x:CdOrPrtry/x:Cd", namespace).text == "PRCD":
      date = parse_date(bal_entry.find("./x:Dt/x:Dt", namespace).text)
      balance = read_amount(bal_entry, namespace)
  ntry_entries = root.findall("./x:BkToCstmrStmt/x:Stmt/x:Ntry", namespace)
  for key, group in itertools.groupby(ntry_entries, key = lambda x: x.find("./x:BookgDt/x:Dt", namespace).text):
    next_date = parse_date(key) + datetime.timedelta(days = 1)
    add_balance(statement["balances"], date, balance, next_date)
    date = next_date
    balance = round(balance + sum(read_amount(x, namespace) for x in group), 2)
  for bal_entry in bal_entries:
    if bal_entry.find("./x:Tp/x:CdOrPrtry/x:Cd", namespace).text == "CLBD":
      next_date = parse_date(bal_entry.find("./x:Dt/x:Dt", namespace).text) + datetime.timedelta(days = 2)
  add_balance(statement["balances"], date, balance, next_date)
  for ntry_entry in ntry_entries:
    amount = read_amount(ntry_entry, namespace)
    if amount > 0:
      date = parse_date(ntry_entry.find("./x:BookgDt/x:Dt", namespace).text)
      account_number_entries = ntry_entry.findall("./x:NtryDtls/x:TxDtls/x:RltdPties/x:DbtrAcct/x:Id/x:Othr/x:Id", namespace)
      bank_code_entries = ntry_entry.findall("./x:NtryDtls/x:TxDtls/x:RltdAgts/x:DbtrAgt/x:FinInstnId/x:Othr/x:Id", namespace)
      if account_number_entries and bank_code_entries:
        account = account_number_entries[0].text + "/" + bank_code_entries[0].text
        statement["incomes"].append({"date": date, "amount": amount, "account": account})
  return statement

def process_statement_moneta(root):
  statement = {"account": None, "balances": {}, "incomes": []}
  iban = root.find("./header/account").attrib["iban"]
  statement["account"] = convert_iban(iban)
  date = parse_date(root.find("./header/stmt").attrib["date-previous"]) + datetime.timedelta(days = 1)
  balance = float(root.find("./header/account/stm-bgn-bal").text)
  transactions = root.find("./transactions")
  for key, group in itertools.groupby(transactions, key = lambda x: x.attrib["date-eff"]):
    next_date = parse_date(key) + datetime.timedelta(days = 1)
    add_balance(statement["balances"], date, balance, next_date)
    date = next_date
    balance = round(balance + sum(float(x.attrib["amount"]) for x in group), 2)
  next_date = parse_date(root.find("./header/stmt").attrib["date"]) + datetime.timedelta(days = 2)
  add_balance(statement["balances"], date, balance, next_date)
  for transaction in transactions:
    amount = float(transaction.attrib["amount"])
    if amount > 0:
      date = parse_date(transaction.attrib["date-eff"])
      account = transaction.attrib["other-account-number"]
      if account:
        statement["incomes"].append({"date": date, "amount": amount, "account": account})
  return statement

def process_statement(file):
  tree = xml.etree.ElementTree.parse(file)
  root = tree.getroot()
  if root.tag.startswith("{urn:iso:std:iso:20022:tech:xsd:camt."):
    return process_statement_camt(root)
  if root.tag == "statement":
    return process_statement_moneta(root)
  raise Exception("Unknown document")

def match_periods(statement):
  matches = {"balances": [], "incomes": []}
  for date in statement["balances"]:
    period = flask.g.database.get_period_by_start_date(date)
    if period:
      matches["balances"].append({"period_id": period["id"], "balance": statement["balances"][date], "account": statement["account"]})
  for income in statement["incomes"]:
    period = flask.g.database.get_period_for_date(income["date"])
    if period:
      matches["incomes"].append({"period_id": period["id"], **income})
  return matches

def format_period(period):
  return datetime.datetime.strptime(period["start_date"], "%Y-%m-%d %H:%M:%S").strftime("%m / %Y")

@bp.route("/")
def index():
  with database.Database() as flask.g.database:
    matches = None
    data = flask.request.args.get("data", "")
    if data:
      matches = pickle.loads(base64.b64decode(data))
    context = {
      "data": data,
      "matches": matches,
      "list_persons": flask.g.database.list_persons,
      "list_accounts": flask.g.database.list_accounts,
      "list_contracts": flask.g.database.list_contracts,
      "get_period": flask.g.database.get_period,
      "format_period": format_period
    }
    return flask.render_template("upload.html", **context)

@bp.route("/upload_file", methods=["POST"])
def upload_file():
  with database.Database() as flask.g.database:
    file = flask.request.files["file"]
    statement = process_statement(file)
    matches = match_periods(statement)
    data = base64.b64encode(pickle.dumps(matches))
    return flask.redirect(flask.url_for(".index", data = data))

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
    return flask.redirect(flask.url_for(".index", data = flask.request.form["data"]))

@bp.route("/set_income", methods=["POST"])
def set_income():
  with database.Database() as flask.g.database:
    contract_id = int(flask.request.form["contract_id"])
    period_id = int(flask.request.form["period_id"])
    amount = float(flask.request.form["amount"])
    flask.g.database.set_income(contract_id, period_id, amount)
    period = flask.g.database.get_period(period_id)
    calculator.update_differences(period)
    return flask.redirect(flask.url_for(".index", data = flask.request.form["data"]))
