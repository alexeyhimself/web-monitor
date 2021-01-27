import time

import logging
logger = logging.getLogger("monitor")
from libs.logger_loader import *

from libs.config_loader import load_config
from libs.urls_caller import monitor_url
from libs.kafka_sender import process_pre_kafka_queue

from multiprocessing import Process, JoinableQueue


def start_monitor():
  logger.info("Monitor service has been started")

  cfg = load_config()

  monitored_urls = cfg.get("monitored_urls", [])
  if monitored_urls:
    pre_kafka_queue = JoinableQueue()

    procs = []
    for each_url in monitored_urls:
      proc = Process(target=monitor_url, args=(each_url, pre_kafka_queue,))
      procs.append(proc)
      proc.start()
      time.sleep(0.01)  # throtling to diffuse network burst on service start

    kafka_cfg = cfg.get("kafka", {})
    process_pre_kafka_queue(kafka_cfg, pre_kafka_queue)

    for proc in procs:
      proc.join()

  else:
    logger.error("No URL(s) to monitor in config.json")


if __name__ == '__main__':
  start_monitor()
