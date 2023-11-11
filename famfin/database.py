#!/usr/bin/python3

import os
import sqlite3

class Database:

  def __init__(self):
    self.connection = sqlite3.connect(os.environ["DATABASE_PATH"])
    self.connection.row_factory = sqlite3.Row
    cursor = self.connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("CREATE TABLE IF NOT EXISTS person (id INTEGER PRIMARY KEY, name STRING)")
    cursor.execute("CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY, person_id INT, name STRING, number STRING, active INT, FOREIGN KEY (person_id) REFERENCES person(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS contract (id INTEGER PRIMARY KEY, person_id INT, name STRING number STRING, active INT, FOREIGN KEY (person_id) REFERENCES person(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS period (id INTEGER PRIMARY KEY, start_date STRING, UNIQUE (start_date))")
    cursor.execute("CREATE TABLE IF NOT EXISTS statement (id INTEGER PRIMARY KEY, account_id INT, period_id INT, opening_balance INT, FOREIGN KEY (account_id) REFERENCES account(id), FOREIGN KEY (period_id) REFERENCES period(id), UNIQUE (account_id, period_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY, contract_id INT, period_id INT, amount INT, FOREIGN KEY (contract_id) REFERENCES contract(id), FOREIGN KEY (period_id) REFERENCES period(id), UNIQUE (contract_id, period_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS exclusion (id INTEGER PRIMARY KEY, person_id INT, period_id INT, amount INT, description STRING, FOREIGN KEY (person_id) REFERENCES person(id), FOREIGN KEY (period_id) REFERENCES period(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS repayment (id INTEGER PRIMARY KEY, person_id INT, period_id INT, amount INT, description STRING, FOREIGN KEY (person_id) REFERENCES person(id), FOREIGN KEY (period_id) REFERENCES period(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS difference (id INTEGER PRIMARY KEY, person_id INT, period_id INT, amount INT, FOREIGN KEY (person_id) REFERENCES person(id), FOREIGN KEY (period_id) REFERENCES period(id), UNIQUE (person_id, period_id))")
    self.connection.commit()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.connection.close()
    self.connection = None

  def list_persons(self):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, name FROM person ORDER BY name")
    return cursor.fetchall()

  def list_accounts(self, person_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, person_id, name, number, active FROM account WHERE person_id = ? ORDER BY name", (person_id, ))
    return cursor.fetchall()

  def list_contracts(self, person_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, person_id, name, number, active FROM contract WHERE person_id = ? ORDER BY name", (person_id, ))
    return cursor.fetchall()

  def list_periods(self):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, start_date FROM period ORDER BY datetime(start_date)")
    return cursor.fetchall()

  def get_period(self, id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, start_date FROM period WHERE id = ?", (id, ))
    return cursor.fetchone()

  def get_current_period(self):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, start_date FROM period WHERE datetime(start_date) <= datetime('now') ORDER BY datetime(start_date) DESC LIMIT 1")
    return cursor.fetchone()

  def get_next_period(self, id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT p1.id, p1.start_date FROM period AS p1 JOIN period AS p2 ON datetime(p1.start_date) > datetime(p2.start_date) WHERE p2.id = ? ORDER BY datetime(p1.start_date) LIMIT 1", (id, ))
    return cursor.fetchone()

  def get_prev_period(self, id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT p1.id, p1.start_date FROM period AS p1 JOIN period AS p2 ON datetime(p1.start_date) < datetime(p2.start_date) WHERE p2.id = ? ORDER BY datetime(p1.start_date) DESC LIMIT 1", (id, ))
    return cursor.fetchone()

  def get_period_for_date(self, date):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, start_date FROM period WHERE datetime(start_date) <= datetime(?) ORDER BY datetime(start_date) DESC LIMIT 1", (date, ))
    return cursor.fetchone()

  def get_period_by_start_date(self, start_date):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, start_date FROM period WHERE datetime(start_date) = datetime(?)", (start_date, ))
    return cursor.fetchone()

  def get_statement(self, account_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, account_id, period_id, opening_balance FROM statement WHERE account_id = ? AND period_id = ?", (account_id, period_id))
    return cursor.fetchone()

  def get_statements_sum(self, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(opening_balance) FROM statement WHERE period_id = ?", (period_id, ))
    return cursor.fetchone()[0] or 0

  def get_person_statements_sum(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(statement.opening_balance) FROM statement JOIN account ON statement.account_id = account.id WHERE account.person_id = ? AND statement.period_id = ?", (person_id, period_id))
    return cursor.fetchone()[0] or 0

  def get_income(self, contract_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, contract_id, period_id, amount FROM income WHERE contract_id = ? AND period_id = ?", (contract_id, period_id))
    return cursor.fetchone()

  def get_incomes_sum(self, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM income WHERE period_id = ?", (period_id, ))
    return cursor.fetchone()[0] or 0

  def get_person_incomes_sum(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(income.amount) FROM income JOIN contract ON income.contract_id = contract.id WHERE contract.person_id = ? AND income.period_id = ?", (person_id, period_id))
    return cursor.fetchone()[0] or 0

  def list_exclusions(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, person_id, period_id, amount, description FROM exclusion WHERE person_id = ? AND period_id = ? ORDER BY description", (person_id, period_id))
    return cursor.fetchall()

  def get_exclusion(self, id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, person_id, period_id, amount, description FROM exclusion WHERE id = ?", (id, ))
    return cursor.fetchone()

  def get_exclusions_sum(self, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM exclusion WHERE period_id = ?", (period_id, ))
    return cursor.fetchone()[0] or 0

  def get_person_exclusions_sum(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM exclusion WHERE person_id = ? AND period_id = ?", (person_id, period_id))
    return cursor.fetchone()[0] or 0

  def list_repayments(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, person_id, period_id, amount, description FROM repayment WHERE person_id = ? AND period_id = ? ORDER BY description", (person_id, period_id))
    return cursor.fetchall()

  def get_repayment(self, id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT id, person_id, period_id, amount, description FROM repayment WHERE id = ?", (id, ))
    return cursor.fetchone()

  def get_repayments_sum(self, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM repayment WHERE period_id = ?", (period_id, ))
    return cursor.fetchone()[0] or 0

  def get_person_repayments_sum(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM repayment WHERE person_id = ? AND period_id = ?", (person_id, period_id))
    return cursor.fetchone()[0] or 0

  def get_person_differences_sum(self, person_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("SELECT SUM(d.amount) FROM difference AS d JOIN period AS p1 ON d.period_id = p1.id JOIN period AS p2 ON datetime(p1.start_date) <= datetime(p2.start_date) WHERE d.person_id = ? AND p2.id = ?", (person_id, period_id))
    return cursor.fetchone()[0] or 0

  def insert_person(self, name):
    cursor = self.connection.cursor()
    cursor.execute("INSERT INTO person VALUES (NULL, ?)", (name, ))
    self.connection.commit()

  def update_person(self, id, name):
    cursor = self.connection.cursor()
    cursor.execute("UPDATE person SET name = ? WHERE id = ?", (name, id))
    self.connection.commit()

  def delete_person(self, id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM person WHERE id = ?", (id, ))
    self.connection.commit()

  def insert_account(self, person_id, name, number, active):
    cursor = self.connection.cursor()
    cursor.execute("INSERT INTO account VALUES (NULL, ?, ?, ?, ?)", (person_id, name, number, active))
    self.connection.commit()

  def update_account(self, id, name, number, active):
    cursor = self.connection.cursor()
    cursor.execute("UPDATE account SET name = ?, number = ?, active = ? WHERE id = ?", (name, number, active, id))
    self.connection.commit()

  def delete_account(self, id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM account WHERE id = ?", (id, ))
    self.connection.commit()

  def insert_contract(self, person_id, name, number, active):
    cursor = self.connection.cursor()
    cursor.execute("INSERT INTO contract VALUES (NULL, ?, ?, ?, ?)", (person_id, name, number, active))
    self.connection.commit()

  def update_contract(self, id, name, number, active):
    cursor = self.connection.cursor()
    cursor.execute("UPDATE contract SET name = ?, number = ?, active = ? WHERE id = ?", (name, number, active, id))
    self.connection.commit()

  def delete_contract(self, id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM contract WHERE id = ?", (id, ))
    self.connection.commit()

  def insert_period(self, start_date):
    cursor = self.connection.cursor()
    cursor.execute("INSERT INTO period VALUES (NULL, ?)", (start_date, ))
    self.connection.commit()

  def set_statement(self, account_id, period_id, opening_balance):
    cursor = self.connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO statement VALUES (NULL, ?, ?, ?)", (account_id, period_id, opening_balance))
    self.connection.commit()

  def delete_statement(self, account_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM statement WHERE account_id = ? AND period_id = ?", (account_id, period_id))
    self.connection.commit()

  def set_income(self, contract_id, period_id, amount):
    cursor = self.connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO income VALUES (NULL, ?, ?, ?)", (contract_id, period_id, amount))
    self.connection.commit()

  def delete_income(self, contract_id, period_id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM income WHERE contract_id = ? AND period_id = ?", (contract_id, period_id))
    self.connection.commit()

  def insert_exclusion(self, person_id, period_id, amount, description):
    cursor = self.connection.cursor()
    cursor.execute("INSERT INTO exclusion VALUES (NULL, ?, ?, ?, ?)", (person_id, period_id, amount, description))
    self.connection.commit()

  def update_exclusion(self, id, amount, description):
    cursor = self.connection.cursor()
    cursor.execute("UPDATE exclusion SET amount = ?, description = ? WHERE id = ?", (amount, description, id))
    self.connection.commit()

  def delete_exclusion(self, id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM exclusion WHERE id = ?", (id, ))
    self.connection.commit()

  def insert_repayment(self, person_id, period_id, amount, description):
    cursor = self.connection.cursor()
    cursor.execute("INSERT INTO repayment VALUES (NULL, ?, ?, ?, ?)", (person_id, period_id, amount, description))
    self.connection.commit()

  def update_repayment(self, id, amount, description):
    cursor = self.connection.cursor()
    cursor.execute("UPDATE repayment SET amount = ?, description = ? WHERE id = ?", (amount, description, id))
    self.connection.commit()

  def delete_repayment(self, id):
    cursor = self.connection.cursor()
    cursor.execute("DELETE FROM repayment WHERE id = ?", (id, ))
    self.connection.commit()

  def set_difference(self, person_id, period_id, amount):
    cursor = self.connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO difference VALUES (NULL, ?, ?, ?)", (person_id, period_id, amount))
    self.connection.commit()

  def dump(self):
    return self.connection.iterdump()
