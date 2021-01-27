import sys
import json
from kafka import KafkaProducer

import logging
logger = logging.getLogger(__name__)


def init_kafka_producer(cfg):
  host = cfg.get("host", "")
  port = cfg.get("port", "")
  server = host + ':' + port

  try:
    producer = KafkaProducer(
      bootstrap_servers=server,
      security_protocol="SSL",
      ssl_cafile=cfg.get("ssl_cafile"),
      ssl_certfile=cfg.get("ssl_certfile"),
      ssl_keyfile=cfg.get("ssl_keyfile"),
      value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

  except Exception as why:
    logger.error(str(why), exc_info=True)
    sys.exit()


def process_pre_kafka_queue(cfg, queue):
  producer = init_kafka_producer(cfg)
  topic = cfg.get("topic", "")

  while True:
    try:
      report_item = queue.get()
      if report_item:
        producer.send(topic, report_item)
        producer.flush()
        queue.task_done()

    except Exception as why:
      logger.error(str(why), exc_info=True)
      sys.exit()
