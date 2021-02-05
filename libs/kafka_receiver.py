import sys
import json
import time
from kafka import KafkaConsumer

from libs.db_sender import save_reports_to_db

import logging
logger = logging.getLogger(__name__)


# Tries to establish consumer connection to Kafka based on config.json params
# If fails then exits, because it is unrecoverable failure
# If succeeds then returns cunsumer and topic
def init_kafka_consumer(cfg):
  logger.info("Starting Kafka consumer connector...")

  kafka_cfg = cfg.get("kafka", {})

  host = kafka_cfg.get("host", "")
  port = kafka_cfg.get("port", "")
  server = host + ':' + port
  topic = kafka_cfg.get("topic")

  # Examples of configuration were given from:
  # https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
  # https://pypi.org/project/kafka-python/
  try:
    consumer = KafkaConsumer(
      topic,
      auto_offset_reset="earliest",
      enable_auto_commit=False,
      bootstrap_servers=server,
      client_id="web-monitor-client-1",
      group_id="web-monitor-group-1",
      security_protocol="SSL",
      ssl_cafile=kafka_cfg.get("ssl_cafile"),
      ssl_certfile=kafka_cfg.get("ssl_certfile"),
      ssl_keyfile=kafka_cfg.get("ssl_keyfile"),
      value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    consumer.poll(timeout_ms=1000)  # initial call will assign partitions
                                    # without retreiving anything and commits
    return consumer, topic

  except Exception as why:
    msg = "Monitor service will not be started! \n"
    msg += "Could not init producer due to an error: "
    logger.critical(msg, exc_info=True)
    sys.exit()  # exit, because unrecoverable failure


def check_queue_and_send_to_db(consumer, topic, cfg):
  logger.info("Starting Kafka queue processing...")

  db_cfg = cfg.get("db", {})

  while True:
    report_items = consumer.poll(timeout_ms=1000)
    if report_items:
      logger.info("Just received from Kafka reports.")
      for tp, msgs in report_items.items():
        save_reports_to_db(db_cfg, msgs, topic)
        consumer.commit()  # commit only if DB saved without errors

    else:
      logger.info("Nothing received from Kafka yet.")


# Every 1 second (timeout_ms is defined in consumer.poll) tries to poll 
# reports from Kafka queue. If Kafka is unavailable, tries to 
# poll reports with throtling timeout (10s). Never ends.
def backup_kafka_to_db(cfg):
  logger.info("Starting Kafka to PostgreSQL backup...")

  consumer, topic = init_kafka_consumer(cfg)
  try:
    check_queue_and_send_to_db(consumer, topic, cfg)

  except Exception as why:
    logger.error(str(why), exc_info=True)
    msg = "Waiting for a throtling period to allow Kafka or DB to recover."
    logger.info(msg)
    time.sleep(10)  # requests throtling
