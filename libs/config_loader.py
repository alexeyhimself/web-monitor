import sys
import json
import os.path

import logging
logger = logging.getLogger(__name__)

CONFIG_PATH = 'configs/config.json'
CONFIG_PATH_DEV = 'configs/config.dev.json'


def load_config():
  # For dev and test purposes CONFIG_PATH_DEV file has higher priority over 
  # CONFIG_PATH. CONFIG_PATH_DEV file also is in .gitignore
  if os.path.isfile(CONFIG_PATH_DEV):
    cfg_path = CONFIG_PATH_DEV
  else:
    cfg_path = CONFIG_PATH

  try:
    with open(cfg_path) as file:
      cfg_file = file.read()
    cfg = json.loads(cfg_file)
    return cfg

  except Exception as why:
    err_msg = "Could not load config file due to an error: " + str(why)
    logger.critical(err_msg)
    sys.exit()
