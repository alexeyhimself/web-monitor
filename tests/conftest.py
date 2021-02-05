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
