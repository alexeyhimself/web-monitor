import sys
import json
import os.path

import logging
logger = logging.getLogger(__name__)

# For dev and test purposes CONFIG_PATH_DEV file has higher priority over 
# CONFIG_PATH. CONFIG_PATH_DEV file also is in .gitignore
CONFIG_PATH = 'configs/config.json'
CONFIG_PATH_DEV = 'configs/config.dev.json'
cfg_path = CONFIG_PATH_DEV if os.path.isfile(CONFIG_PATH_DEV) else CONFIG_PATH


def load_config():
  try:
    with open(cfg_path) as file:
      cfg_file = file.read()
    cfg = json.loads(cfg_file)
    return cfg

  except Exception as why:
    err_msg = "Could not load config file due to an error: " + str(why)
    logger.critical(err_msg)
    sys.exit()
