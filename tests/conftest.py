import pytest
import psycopg2
from contextlib import closing

from libs.config_loader import load_config, validate_cfg


# clone from libs.apply_to_db made for tests
def apply_sql_to_db(db_cfg, sql):
  conn = psycopg2.connect(
    dbname=db_cfg.get("db_name"),
    user=db_cfg.get("user"),
    password=db_cfg.get("password"), 
    host=db_cfg.get("host"),
    port=db_cfg.get("port"),
    sslmode=db_cfg.get("sslmode"),
    sslrootcert=db_cfg.get("sslrootcert")
  )

  with closing(conn) as c:
    with c.cursor() as cursor:
      cursor.execute(sql)


def get_cfg_part(part):
  cfg = load_config()
  validate_cfg(cfg)
  return cfg.get(part, {})


def cleanup_db():
  db_cfg = get_cfg_part('db_pytest')
  sql = "DELETE FROM web_monitoring WHERE url = 'http://pytest'; COMMIT;"
  apply_sql_to_db(db_cfg, sql)


@pytest.fixture(scope="session")
def prepare_db():
  # setup
  cleanup_db()

  yield

  # teardown
  pass


from attrdict import AttrDict
report = {"url": "http://pytest", "event_date": None, "is_fine": True,
          "transport": "pytest_transport", "response_code": 0, "response_time": 0.1,
          "regexp": "string", "regexp_found": True, "timeout": 1.1, 
          "period": 2.2}


def form_post_kafka_reports():
  attr_dict = AttrDict({'value': report})  # need this because kafka sends
                                           # reports in .value attributes
  return [attr_dict]


from multiprocessing import JoinableQueue


def form_pre_kafka_queue():
  pre_kafka_queue = JoinableQueue()
  pre_kafka_queue.put(report)
  return pre_kafka_queue, report
