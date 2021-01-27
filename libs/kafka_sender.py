import logging
logger = logging.getLogger(__name__)


def process_pre_kafka_queue(queue):
  while True:
    item = queue.get()
    logger.info(item)
    queue.task_done()
