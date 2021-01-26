import logging
logger = logging.getLogger("monitor")
from libs.logger_loader import *

from libs.config_loader import load_config
from libs.urls_caller import monitor_url

from multiprocessing import Process


def start_monitor():
  logger.info("Monitor service has been started")

  cfg = load_config()

  monitored_urls = cfg.get("monitored_urls", [])
  if monitored_urls:
    procs = []
    for each_url in monitored_urls:
      proc = Process(target=monitor_url, args=(each_url,))
      procs.append(proc)
      proc.start()

    for proc in procs:
      proc.join()

  else:
    logger.error("No URL(s) to monitor in config.json")


if __name__ == '__main__':
  start_monitor()
