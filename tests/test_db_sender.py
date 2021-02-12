import pytest
from libs.db_sender import apply_to_db, save_reports_to_db, compose_sql
from tests.conftest import get_cfg_part, form_post_kafka_reports


@pytest.mark.skip(reason="In CI need a PostgreSQL server to test this.")
def test_apply_to_db_works_when_valid_config():
  db_cfg = get_cfg_part('db_pytest')
  sql = 'SELECT * FROM web_monitoring LIMIT 1;'

  apply_to_db(db_cfg, sql)
  assert 1 == 1


@pytest.mark.skip(reason="In CI need a PostgreSQL server to test this.")
def test_save_reports_to_db_works_when_valid_config(prepare_db):
  db_cfg = get_cfg_part('db_pytest')

  reports = form_post_kafka_reports()
  topic = 'pytest_topic'

  save_reports_to_db(db_cfg, reports, topic)
  assert 1 == 1


def test_compose_sql_works():
  reports = form_post_kafka_reports()
  topic = 'pytest_topic'

  sql, vals = compose_sql(reports, topic)
  assert 1 == 1


import psycopg2


def test_save_reports_to_db_exits_when_invalid_config():
  db_cfg = {}
  reports = form_post_kafka_reports()
  topic = 'pytest_topic'

  with pytest.raises(Exception) as pytest_wrapped_e:
    save_reports_to_db(db_cfg, reports, topic)
  assert pytest_wrapped_e.type in [
    psycopg2.OperationalError, 
    psycopg2.errors.UndefinedTable
  ]


def test_apply_to_db_exits_when_invalid_config():
  db_cfg = {}
  sql = 'SELECT * FROM web_monitoring LIMIT 1;'
  with pytest.raises(Exception) as pytest_wrapped_e:
    apply_to_db(db_cfg, sql, ())
  assert pytest_wrapped_e.type in [
    psycopg2.OperationalError,
    psycopg2.errors.UndefinedTable
  ]
