import pytest
from libs.db_sender import to_sql, apply_to_db, save_reports_to_db, compose_sql


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


from tests.conftest import get_cfg_part
from attrdict import AttrDict


@pytest.mark.skip(reason="In CI need a PostgreSQL server to test this.")
def test_apply_to_db_works_when_valid_config():
  db_cfg = get_cfg_part('db_pytest')
  sql = 'SELECT * FROM web_monitoring LIMIT 1;'

  apply_to_db(db_cfg, sql)
  assert 1 == 1


def form_post_kafka_reports():
  report = {"url": "http://pytest", "event_date": None, "is_fine": True,
            "transport": "pytest", "response_code": 0, "response_time": 0.1, 
            "regexp": "string", "regexp_found": True, "timeout": 1.1, "period": 2.2}
  attr_dict = AttrDict({'value': report})  # need this because kafka sends
                                           # reports in .value attributes
  return [attr_dict]


@pytest.mark.skip(reason="In CI need a PostgreSQL server to test this.")
def test_save_reports_to_db_works_when_valid_config(prepare_db):
  db_cfg = get_cfg_part('db_pytest')

  reports = form_post_kafka_reports()
  topic = 'pytest'

  save_reports_to_db(db_cfg, reports, topic)
  assert 1 == 1


def test_compose_sql_works():
  reports = form_post_kafka_reports()
  topic = 'pytest'

  compose_sql(reports, topic)
  assert 1 == 1


import psycopg2


def test_save_reports_to_db_exits_when_invalid_config():
  db_cfg = {}
  reports = form_post_kafka_reports()
  topic = 'pytest'

  with pytest.raises(Exception) as pytest_wrapped_e:
    save_reports_to_db(db_cfg, reports, topic)
  assert pytest_wrapped_e.type == psycopg2.OperationalError

@pytest.mark.d
def test_apply_to_db_exits_when_invalid_config():
  db_cfg = {}
  sql = 'SELECT * FROM web_monitoring LIMIT 1;'
  with pytest.raises(Exception) as pytest_wrapped_e:
    apply_to_db(db_cfg, sql)
  assert pytest_wrapped_e.type == psycopg2.OperationalError
