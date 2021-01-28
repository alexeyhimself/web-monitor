import sys
import json
from kafka import KafkaConsumer

import logging
logger = logging.getLogger(__name__)


# Tries to establish consumer connection to Kafka based on config.json params
def init_kafka_consumer(cfg):
  logger.info("Starting Kafka consumer connector...")

  kafka_cfg = cfg.get("kafka")

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
      bootstrap_servers=server,
      client_id="demo-client-1",
      group_id="demo-group",
      security_protocol="SSL",
      ssl_cafile=kafka_cfg.get("ssl_cafile"),
      ssl_certfile=kafka_cfg.get("ssl_certfile"),
      ssl_keyfile=kafka_cfg.get("ssl_keyfile")
    )

    consumer.poll(timeout_ms=1000)  # initial call will assign partitions
                                    # without retreiving anything and commits
    return consumer

  except Exception as why:
    logger.critical(str(why), exc_info=True)
    sys.exit()  # exit, because unrecoverable failure


# Every 1 second (timeout_ms is defined in consumer.poll) tries to poll 
# reports from Kafka queue. If Kafka is unavailable, tries to 
# poll reports with 30s throtling.
def backup_kafka_to_db(cfg):
  logger.info("Starting Kafka to PostgreSQL backup...")

  consumer = init_kafka_consumer(cfg)

  logger.info("Starting Kafka queue processing...")

  # INFO log is silent if everything is fine.
  # I want to see something in logs sometimes, that everything is fine
  # and the service is working.
  kafka_reports_cnt = 0
  kafka_polls = 0
  notify_in_polls = 1

  while True:
    try:
      report_items = consumer.poll(timeout_ms=1000)
      if report_items:
        for tp, msgs in report_items.items():
          for msg in msgs:
            logger.debug("Received: {}".format(msg.value))
            kafka_reports_cnt += 1

        kafka_polls += 1
        consumer.commit()

        if kafka_polls % notify_in_polls == 0:
          msg = "Service is alive, by this time "
          msg += "received from Kafka %s polls." % kafka_polls
          logger.info(msg)

        msg = "Just received from Kafka %s reports." % kafka_reports_cnt
        logger.info(msg)
      else:
        msg = "Nothing to receive from Kafka yet."
        logger.info(msg)

    except Exception as why:
      logger.error(str(why), exc_info=True)
      time.sleep(30)  # requests throtling in case of Kafka unavailable
