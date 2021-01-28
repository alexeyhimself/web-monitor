import sys
import json
import time
import multiprocessing
from kafka import KafkaProducer

import logging
logger = logging.getLogger(__name__)


# Tries to establish producer connection to Kafka based on config.json params
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
    logger.critical(str(why), exc_info=True)
    sys.exit()  # exit, because unrecoverable failure


# Dumps up to 10000 records (qsize does not work on MacOS) from queue
# within buffering_timeout seconds and returns that dump list
def dump_queue(queue):
  buffering_timeout = 1  # [seconds]
  result = []
  try:
    for i in range(10000):
      report_item = queue.get(timeout=buffering_timeout)
      if report_item:
        result.append(report_item)

  except multiprocessing.queues.Empty:
    pass  # all queue reports already given

  return result


# Every 1 second (buffering_timeout is defined in dump_queue) tries to send 
# reports from pre-Kafka queue to Kafka. If Kafka is unavailable, tries to 
# send reports with 30s throtling.
def process_pre_kafka_queue(cfg, queue):
  logger.info("Starting pre-Kafka queue processor...")

  producer, topic = init_kafka_producer(cfg)

  logger.info("Starting pre-Kafka queue processing...")

  # INFO log is silent if everything is fine.
  # I want to see something in logs sometimes, that everything is fine
  # and the service is working.
  kafka_flushes = 0
  notify_in_flushes = 10

  while True:
    try:
      report_items = dump_queue(queue)
      if report_items:
        for each_report in report_items:
          producer.send(topic, each_report)

        producer.flush()
        kafka_flushes += 1

        queue.task_done()

        if kafka_flushes % notify_in_flushes == 0:
          msg = "Service is alive, "
          msg += "by this time flushed to Kafka %s times." % kafka_flushes
          logger.info(msg)

        msg = "Just sent to Kafka %s reports." % len(report_items)
        logger.info(msg)
      else:
        msg = "Nothing to send to Kafka yet."
        logger.info(msg)

    except Exception as why:
      logger.error(str(why), exc_info=True)
      logger.info("Waiting for a throtling period to allow Kafka to recover.")
      time.sleep(30)  # requests throtling in case of Kafka unavailable
