import sys
import json
from kafka import KafkaProducer

import logging
logger = logging.getLogger(__name__)


def init_kafka_producer(cfg):
  logger.info("Starting Kafka producer connector...")

  kafka_cfg = cfg.get("kafka")
  host = kafka_cfg.get("host", "")
  port = kafka_cfg.get("port", "")
  server = host + ':' + port
  topic = kafka_cfg.get("topic")

  # Examples of configuration were given from:
  # https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
  # https://pypi.org/project/kafka-python/
  try:
    producer = KafkaProducer(
      bootstrap_servers=server,
      security_protocol="SSL",
      ssl_cafile=kafka_cfg.get("ssl_cafile"),
      ssl_certfile=kafka_cfg.get("ssl_certfile"),
      ssl_keyfile=kafka_cfg.get("ssl_keyfile"),
      value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer, topic

  except Exception as why:
    logger.error(str(why), exc_info=True)
    sys.exit()  # exit, because unrecoverable failure


def process_pre_kafka_queue(cfg, queue):
  logger.info("Starting pre-Kafka queue processor...")

  producer, topic = init_kafka_producer(cfg)

  # INFO log is silent if everything is fine.
  # I want to see something in log sometimes, that everything is fine.
  monitored_urls = cfg.get("monitored_urls", [])
  log_service_alive_every = len(monitored_urls) * 10

  logger.info("Starting pre-Kafka queue processing...")
  report_items = 0
  while True:
    try:
      report_item = queue.get()
      if report_item:
        producer.send(topic, report_item)
        producer.flush()
        queue.task_done()
        report_items += 1

      if report_items % log_service_alive_every == 0:
        msg = "Service is alive, "
        msg += "by this time sent to Kafka %s reports." % report_items
        logger.info(msg)

    except Exception as why:
      logger.error(str(why), exc_info=True)
      sys.exit()  # exit, because unrecoverable failure
