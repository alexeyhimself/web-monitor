import sys
import json

CONFIG_PATH = 'config.json'


def load_config():
  try:
    with open(CONFIG_PATH) as file:
      cfg_file = file.read()
    cfg = json.loads(cfg_file)
    return cfg

  except Exception as why:
    err_msg = "Could not load config file due to an error: " + str(why)
    print(err_msg)
    sys.exit()
