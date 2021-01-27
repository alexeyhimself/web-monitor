import logging
logger = logging.getLogger(__name__)


def put_to_kafka_queue(report):
  logger.info(report)
