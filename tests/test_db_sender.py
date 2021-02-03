import pytest
from libs.db_sender import to_sql


def test_to_sql_string():
  sql = to_sql("string")
  assert sql == "'string'"


def test_to_sql_1():
  sql = to_sql(1)
  assert sql == "1"


def test_to_sql_0():
  sql = to_sql(0)
  assert sql == "0"


def test_to_sql_None():
  sql = to_sql(None)
  assert sql == "NULL"


def test_to_sql_False():
  sql = to_sql(False)
  assert sql == "False"


def test_to_sql_True():
  sql = to_sql(True)
  assert sql == "True"
