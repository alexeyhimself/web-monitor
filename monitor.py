import time

import logging
logger = logging.getLogger("monitor")
from libs.logger_loader import *

from libs.config_loader import load_config, validate_cfg
from libs.urls_caller import monitor_url
from libs.kafka_sender import process_pre_kafka_queue
from libs.local_debug_loader import ld_cfg

from multiprocessing import Process, JoinableQueue

import signal, sys


# Starts Monitor service: loads and validates config, starts monitors processes 
# (process per URL), starts pre-Kafka queue and starts that queue processor 
# (Kafka producer).
# If any init procedure fails, service exits with reason description in logs.
def start_monitor(cfg):
  logger.info("Starting monitor service...")

  # init queue for storing monitoring records before sending them to kafka 
  # (in order not to loose monitoring data if kafka unavailable)
  pre_kafka_queue = JoinableQueue()

  monitored_urls = cfg.get("monitored_urls", [])
  # starting URLs monitoring (process per URL)
  logger.info("Starting URL(s) monitoring...")
  for each_url in monitored_urls:
    proc = Process(
      target=monitor_url, 
      args=(each_url, pre_kafka_queue,)
    )
    proc.start()
    time.sleep(0.01)  # throtling to diffuse network burst on service start
                      # in case of hundreds/thousands of monitored URLs

  logger.info("URL(s) monitoring has been started.")

  process_pre_kafka_queue(cfg, pre_kafka_queue)

  # we do not need proc joins because if process_pre_kafka_queue exits
  # we need to exit as well
  """
  for proc in procs:
    proc.join()
  """


from libs.kafka_receiver import backup_kafka_to_db


def start_kafka_to_db(cfg):
  logger.info("Starting Kafka to PostgreSQL backup service...")

  backup_kafka_to_db(cfg)


def keyboard_interruption_handler(signum, frame):
  logger.info("Monitor service process has been stopped.")
  sys.exit()


if __name__ == '__main__':
  signal.signal(signal.SIGINT, keyboard_interruption_handler)

  cfg = load_config()
  validate_cfg(cfg)

  # .local_debug's mode priority
  dev_mode = ld_cfg.get("mode")
  if dev_mode:
    if dev_mode == "backup":
      start_kafka_to_db(cfg)
    elif dev_mode == "monitor":
      start_monitor(cfg)

  else:
    mode = cfg.get("mode")
    if mode == "backup":
      start_kafka_to_db(cfg)
    elif mode == "monitor":
      start_monitor(cfg)

