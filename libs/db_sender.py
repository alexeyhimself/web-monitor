from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import psycopg2
from contextlib import closing


# Translates Python data values to SQL values.
# For example, None to NULL, abc to 'abc'...
def to_sql(item):
  if item:
    if isinstance(item, str):
      return "'" + item + "'"
    else:  # True, number != 0 for example
      return str(item)
  else:
    if item is None:  # special value
      return "NULL"
    else:  # False, number == 0 for example
      return str(item)


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

    values = []
    for each_col in table_cols:
      value = to_sql(r.get(each_col))
      values.append(value)

    item = "INSERT INTO web_monitoring (" + ",".join(table_cols) + ") "
    item += "VALUES (" + ",".join(values) + ");"

    sql += item

  sql += "COMMIT;"
  return sql


# Gets decoded reports list of dicts from Kafka and tries to save them all
# in DB under the same transaction. If transaction fails, exception is passed
# to a caller function, whole reports list is not commited.
def save_reports_to_db(db_cfg, reports, topic):
  msg = "Saving to DB %s reports..." % len(reports)
  logger.info(msg)

  sql = compose_sql(reports, topic)
  apply_to_db(db_cfg, sql)


# Establishes connection to DB and executes given sql on DB
# If exception, then it is passed to a caller function
# Used materials from: https://khashtamov.com/ru/postgresql-python-psycopg2
def apply_to_db(db_cfg, sql):
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
      cursor.execute(sql)
