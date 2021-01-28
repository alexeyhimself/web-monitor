# do not log requests, urllib3, kafka in DEBUG/INFO level
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)


# .local_debug file that is in .gitignore that helps to distinguish:
# DEV or PRO machine and provides options for fast switching of configuration.
# For example, changing log_level (to see what PRO logs will look like to make) 
# them more comprehensive or add more log details when developing features 
# without changing this file. 
import os.path
from libs.config_loader import load_config
ld_path = '.local_debug'

if os.path.isfile(ld_path):
  DEBUG = True
  ld_cfg = load_config(ld_path)
else:
  DEBUG = False

handler = ld_cfg.get("log_handler", "console") if DEBUG == True else "file"
level = ld_cfg.get("log_level", "DEBUG") if DEBUG == True else "INFO"


# Logs output customization and applying
from logging.config import dictConfig

log_format = "%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s.py | "
log_format += "%(funcName)s: %(lineno)s | %(message)s"

logging_config = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'verbose': {
      'format': log_format,
      'datefmt': "%Y-%m-%d %H:%M:%S"
    }
  },
  'filters': {
  },
  'handlers': {
    'console': {
      # 'level': 'DEBUG',
      'class': 'logging.StreamHandler',
      'formatter': 'verbose'
    },
    'file': {
      # 'level': 'DEBUG',
      'class': 'logging.handlers.RotatingFileHandler',
      'filename': './monitor.log',
      'maxBytes': 1024*1024*150,  # 15MB
      'backupCount': 10,
      'formatter': 'verbose'
    }
  },
  'loggers': {
    '': {
      'handlers': [handler],
      'level': level
    }
  }
}

dictConfig(logging_config)
