import sys
import json
import time
import multiprocessing
from kafka import KafkaProducer

import logging
logger = logging.getLogger(__name__)


# Tries to establish producer connection to Kafka based on config.json params
# If fails then exits, because it is unrecoverable failure
# If succeeds returns producer and topic
def init_kafka_producer(cfg):
  logger.info("Starting Kafka producer connector...")

  kafka_cfg = cfg.get("kafka", {})
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
    msg = "Monitor service will not be started! \n"
    msg += "Could not init producer due to an error: "
    logger.critical(msg, exc_info=True)
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


def check_queue_and_send_to_kafka(producer, topic, queue):
  logger.info("Starting pre-Kafka queue processing...")

  while True:
    report_items = dump_queue(queue)
    if report_items:
      for each_report in report_items:
        producer.send(topic, each_report)

      producer.flush()
      queue.task_done()

      msg = "Just sent to Kafka %s reports." % len(report_items)
      logger.info(msg)
    else:
      msg = "Nothing to send to Kafka yet."
      logger.info(msg)


# Every 1 second (buffering_timeout is defined in dump_queue) tries to send 
# reports from pre-Kafka queue to Kafka. If Kafka is unavailable, tries to 
# send reports with 30s throtling. Never ends.
def process_pre_kafka_queue(cfg, queue):
  logger.info("Starting pre-Kafka queue processor...")

  producer, topic = init_kafka_producer(cfg)
  try:
    check_queue_and_send_to_kafka(producer, topic, queue)

  except Exception as why:
    logger.error(str(why), exc_info=True)
    logger.info("Waiting for a throtling period to allow Kafka to recover.")
    time.sleep(10)  # requests throtling in case of Kafka unavailable
