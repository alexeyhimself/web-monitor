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

def init_monitoring_table(cfg):
  logger.info("Creating web_monitoring table in DB...")

  sql = "CREATE TABLE IF NOT EXISTS web_monitoring (\
      id            BIGSERIAL,\
      url           TEXT,\
      time          TEXT,\
      time_unix     TIMESTAMP,\
      result        TEXT,\
      transport     TEXT,\
      response_code SMALLINT,\
      response_time REAL,\
      regexp        TEXT,\
      regexp_found  BOOLEAN,\
      timeout       REAL,\
      period        REAL\
    ); COMMIT;"

  is_recoverable = False
  apply_to_db(cfg, sql, is_recoverable)  


#def save_reports_to_db(cfg, reports):
"""
    for each_report in reports:
      report = each_report.value
      logger.info("h")
"""
    
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
