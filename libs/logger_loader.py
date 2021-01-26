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
      'handlers': ['console'],
      'level': 'INFO'
    }
  }
}

dictConfig(logging_config)
