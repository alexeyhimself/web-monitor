import sys
import time

import logging
logger = logging.getLogger(__name__)

import psycopg2

# Used materials from:
# https://khashtamov.com/ru/postgresql-python-psycopg2/
# https://help.compose.com/docs/postgresql-and-python
# https://postgrespro.ru/docs/postgresql/9.6/sql-createtable
# https://postgrespro.ru/docs/postgresql/9.6/datatype-numeric
# https://www.postgresql.org/docs/9.1/sql-createindex.html

def init_monitoring_table(cfg):
  logger.info("Creating web_monitoring table in DB...")
  """
  sql = "DROP table web_monitoring; COMMIT;"
  sql += "CREATE TABLE IF NOT EXISTS web_monitoring (\
      id            BIGSERIAL,\
      url           TEXT,\
      time          TIMESTAMP,\
      time_unix     DOUBLE PRECISION,\
      result        TEXT,\
      transport     TEXT,\
      response_code SMALLINT,\
      response_time REAL,\
      regexp        TEXT,\
      regexp_found  BOOLEAN,\
      timeout       REAL,\
      period        REAL\
    );"

  sql += "ALTER TABLE web_monitoring \
    ADD CONSTRAINT uniq_web_monitoring UNIQUE (\
    url, time_unix, result);"
  
  sql += "CREATE INDEX url_idx_web_monitoring ON web_monitoring (url);"
  sql += "CREATE INDEX result_idx_web_monitoring ON web_monitoring (result);"
  sql += "CREATE INDEX response_code_idx_web_monitoring ON \
    web_monitoring (response_code);"
  sql += "CREATE INDEX regexp_found_idx_web_monitoring ON \
    web_monitoring (regexp_found);"

  sql += "COMMIT;"

  is_recoverable = False
  apply_to_db(cfg, sql, is_recoverable)  
  """

def save_reports_to_db(cfg, reports):
  sql = ""
  for each_report in reports:
    r = each_report.value
    regexp = r.get("regexp")
    if regexp:
      regexp = "'" + regexp + "'"
    else:
      regexp = "NULL"

    item = "INSERT INTO web_monitoring (url, time, time_unix, result, \
    transport, response_code, response_time, regexp, regexp_found, timeout, \
    period) VALUES ('{0}', '{1}', {2}, '{3}', '{4}', {5}, {6}, {7}, {8}, \
    {9}, {10});\
    ".format(r.get("url"), r.get("time"), r.get("time_unix"), 
    r.get("result"), r.get("transport"), r.get("response_code", "NULL"), 
    r.get("response_time", "NULL"), regexp, r.get("regexp_found", "NULL"), 
    r.get("timeout"), r.get("period"))

    logger.debug(item)
    sql += item

  sql += "COMMIT;"
  apply_to_db(cfg, sql)


def apply_to_db(cfg, sql, is_recoverable = True):
  logger.debug("Execute SQL script...")

  db_cfg = cfg.get("db", {})
  db_name = db_cfg.get("db_name")
  user = db_cfg.get("user")
  password = db_cfg.get("password")
  host = db_cfg.get("host")
  port = db_cfg.get("port")
  sslmode = db_cfg.get("sslmode")
  sslrootcert = db_cfg.get("sslrootcert")

  try:
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, 
      host=host, port=port, sslmode=sslmode, sslrootcert=sslrootcert)
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

    # add more db exceptions
  except Exception as why:
    if is_recoverable:
      logger.error(str(why), exc_info=True)
      logger.info("Waiting for a throtling period to allow DB to recover.")
      time.sleep(10)  # requests throtling in case of DB unavailable
    else:
      msg = "Service would not be started due to an error: " + str(why)
      logger.critical(msg, exc_info=True)
      sys.exit()  # exit, because unrecoverable failure
