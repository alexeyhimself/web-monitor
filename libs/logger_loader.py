import logging  # do not log requests, urllib3 in DEBUG/INFO level
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)

import os.path
DEBUG = True if os.path.isfile('.local_debug') else False

handler = 'console' if DEBUG == True else 'file'
level = 'DEBUG' if DEBUG == True else 'INFO'

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
