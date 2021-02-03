import pytest
from libs.db_sender import to_sql, apply_to_db, save_reports_to_db


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


from libs.config_loader import load_config, validate_cfg
from attrdict import AttrDict


def get_db_cfg():
  cfg = load_config()
  validate_cfg(cfg)
  return cfg.get("db", {})


def test_apply_to_db_works():
  db_cfg = get_db_cfg()
  sql = 'SELECT * FROM web_monitoring LIMIT 1;'

  apply_to_db(db_cfg, sql)
  assert 1 == 1


def test_save_reports_to_db_works():
  db_cfg = get_db_cfg()

  report = {"url": "http://pytest", "event_date": None, "is_fine": True,
            "transport": "pytest", "response_code": 0, "response_time": 0.1, 
            "regexp": "string", "regexp_found": True, "timeout": 1.1, "period": 2.2}
  attr_dict = AttrDict({'value': report})  # need this because kafka sends
                                           # reports in .value attributes
  reports = [attr_dict]
  topic = 'pytest'

  save_reports_to_db(db_cfg, reports, topic)
  assert 1 == 1
