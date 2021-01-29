# Describes logger settings and loads these settings. 
# If .local_debug file exists in project main folder, then by default 
# logs output to console and log level is DEBUG. If not exists then logs
# output to ./logs/monitor.log file with log level INFO.

# do not log requests, urllib3, kafka in DEBUG/INFO level
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)

# ld_cfg is a dict from .local_debug (a file that is in .gitignore and 
# that helps to develop locally and switch parameters without changing
# source code
from libs.local_debug_loader import ld_cfg

DEBUG = True if ld_cfg else False
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
      'class': 'logging.StreamHandler',
      'formatter': 'verbose'
    },
    'file': {
      'class': 'logging.handlers.RotatingFileHandler',
      'filename': './logs/monitor.log',
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
