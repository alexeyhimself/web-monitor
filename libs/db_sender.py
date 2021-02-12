from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import psycopg2
from contextlib import closing


# Translates reports dicts recieved from Kafka to string of SQL 
# statements with 1 trailing commit. Returns that SQL string.
def compose_sql(reports, topic):
  msg = "Compose SQL..."
  logger.debug(msg)

  table_cols = ["topic", "url", "event_date", "is_fine", "transport", 
  "response_code", "response_time", "regexp", "regexp_found", 
  "timeout", "period", "date_created"]

  sql = ""
  for each_report in reports:
    r = each_report.value

    # these columns not originally in report
    r["topic"] = topic
    r["date_created"] = str(datetime.utcnow())

    vals = ()
    values = []
    for each_col in table_cols:
      values.append("%s")
      value = r.get(each_col)
      vals = vals + (value,)

    item = "INSERT INTO web_monitoring (" + ",".join(table_cols) + ") "
    item += "VALUES (" + ",".join(values) + ");"

    sql += item

  return sql, vals


# Gets decoded reports list of dicts from Kafka and tries to save them all
# in DB under the same transaction. If transaction fails, exception is passed
# to a caller function, whole reports list is not commited.
def save_reports_to_db(db_cfg, reports, topic):
  msg = "Saving to DB %s reports..." % len(reports)
  logger.info(msg)

  sql, vals = compose_sql(reports, topic)
  apply_to_db(db_cfg, sql, vals)


# Establishes connection to DB and executes given sql on DB
# If exception, then it is passed to a caller function
# Used materials from: https://khashtamov.com/ru/postgresql-python-psycopg2
def apply_to_db(db_cfg, sql, vals):
  logger.debug("Execute SQL script...")

  # All connectivity and transport exceptions will handled by the upper level 
  # try-catch, because commit to DB must be synced with commit to Kafka
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
      try:
        cursor.execute(sql, vals)
        conn.commit()
      except Exception as why:
        conn.rollback()
        raise why
