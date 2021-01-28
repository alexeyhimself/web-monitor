import sys
import json
import os.path

import logging
logger = logging.getLogger(__name__)

# For dev and test purposes CONFIG_PATH_DEV file has higher priority over 
# CONFIG_PATH. CONFIG_PATH_DEV file also is in .gitignore
CONFIG_PATH = 'configs/config.json'
CONFIG_PATH_DEV = 'configs/config.dev.json'
cp = CONFIG_PATH_DEV if os.path.isfile(CONFIG_PATH_DEV) else CONFIG_PATH


def load_config(cfg_path = cp):
  logger.info("Loading monitor service config...")

  try:
    with open(cfg_path) as file:
      cfg_file = file.read()
    cfg = json.loads(cfg_file)
    return cfg

  except Exception as why:
    err_msg = "Could not load config file due to an error! " + str(why)
    logger.critical(err_msg, exc_info=True)
    sys.exit()  # exit, because unrecoverable failure


DEFAULT_TIMEOUT = 10  # time to wait request response [seconds]
DEFAULT_PERIOD = 60  # time between two consecutive requests [seconds]


def validate_cfg(cfg):
  logger.info("Starting config validation...")

  monitored_urls = cfg.get("monitored_urls", [])

  if monitored_urls:
    for each_url in monitored_urls:
      url = each_url.get("url")
      period = each_url.get("period", DEFAULT_PERIOD)
      timeout = each_url.get("timeout", DEFAULT_TIMEOUT)
      regexp = each_url.get("regexp")

      if not (isinstance(period, int) or isinstance(period, float)):
        msg = "Period must be integer or float. "
        msg += "But for %s it is not: %s. " % (url, period)
        logger.critical(msg, exc_info=True)
        sys.exit()  # exit, because unrecoverable failure

      if not (isinstance(timeout, int) or isinstance(timeout, float)):
        msg = "Timeout must be integer or float. "
        msg += "But for %s it is not: %s. " % (url, timeout)
        logger.critical(msg, exc_info=True)
        sys.exit()  # exit, because unrecoverable failure

      if timeout > period:
        msg = "Timeout can't be greater than period. "
        msg += "But for %s it is: %s > %s. " % (url, timeout, period)
        logger.critical(msg, exc_info=True)
        sys.exit()  # exit, because unrecoverable failure
  else:
    msg = "No URL(s) to monitor in config.json. "
    msg += "Monitor service will not be started!"
    logger.critical(msg, exc_info=True)
    sys.exit()  # exit, because unrecoverable failure
