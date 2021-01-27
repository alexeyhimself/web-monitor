import sys
import time

import logging
logger = logging.getLogger("monitor")
from libs.logger_loader import *

from libs.config_loader import load_config, validate_cfg
from libs.urls_caller import monitor_url
from libs.kafka_sender import init_kafka_producer, process_pre_kafka_queue

from multiprocessing import Process, JoinableQueue


def start_monitor():
  logger.info("Starting monitor service...")

  cfg = load_config()
  validate_cfg(cfg)

  monitored_urls = cfg.get("monitored_urls", [])
  if monitored_urls:
    # init queue for storing monitoring records before sending them to kafka 
    # (in order not to loose monitoring data if kafka unavailable)
    pre_kafka_queue = JoinableQueue()

    # starting urls monitoring (process per url)
    logger.info("Starting URL(s) monitoring...")
    for each_url in monitored_urls:
      proc = Process(
        target=monitor_url, 
        args=(each_url, pre_kafka_queue,)
      )
      proc.start()
      time.sleep(0.01)  # throtling to diffuse network burst on service start

    logger.info("URL(s) monitoring has been started.")

    process_pre_kafka_queue(cfg, pre_kafka_queue)

    # we do not need proc joins because if process_pre_kafka_queue exits
    # we need to exit as well
    """
    for proc in procs:
      proc.join()
    """
  else:
    logger.error("No URL(s) to monitor in config.json")


if __name__ == '__main__':
  start_monitor()
