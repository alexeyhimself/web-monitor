import re
import sys
import time
import requests

import logging
logger = logging.getLogger(__name__)

from multiprocessing import Process
from libs.config_loader import DEFAULT_TIMEOUT, DEFAULT_PERIOD


# Calls specified URL with defined parameters, forms JSON report and
# puts that report to pre-Kafka queue. In case of unrecoverable failure
# sys.exit()'s
def call_url(url, timeout, period, regexp, pre_kafka_queue):
  time_start = time.monotonic()

  report = {
    'url': url,
    'timeout': timeout,
    'period': period,
    'event_date': str(time_start)
  }

  try:
    r = requests.get(url, timeout=timeout)
    time_end = time.monotonic()

    response_time = round(time_end - time_start, 3)

    # overall result to look at, aggregates: 
    # response_code + transport issues + regexp
    is_fine = True if r.status_code == 200 else False
    
    report.update({
      'transport': 'connected',
      'is_fine': is_fine,
      'response_time': response_time,
      'response_code': r.status_code
    })    

    # If HTTP 200 OK and regexp was assigned, then search for regexp and 
    # redefine is_fine based on that search.
    if regexp and r.status_code == 200:
      regexp_found = True if re.search(regexp, r.text) else False
      is_fine = True if regexp_found == True else False

      report.update({
        'regexp': regexp,
        'regexp_found': regexp_found,
        'is_fine': is_fine
      })

  except requests.exceptions.ConnectionError:
    report.update({'transport': 'conn_error', 'is_fine': False})
  except requests.exceptions.Timeout:
    report.update({'transport': 'conn_timeout', 'is_fine': False})
  except Exception as why:
    logger.error(report)
    logger.critical(why, exc_info=True)
    sys.exit()  # don't want to report to Kafka such failed requests

  logger.debug(report)
  pre_kafka_queue.put(report)


# Calls call_url every period. Each period could be defined per URL.
def monitor_url(each_url, pre_kafka_queue):
  url = each_url.get("url")
  period = each_url.get("period", DEFAULT_PERIOD)
  timeout = each_url.get("timeout", DEFAULT_TIMEOUT)
  regexp = each_url.get("regexp")

  # Every period call call_url, which always ends prior period thanks to
  # config validation where must be timeout <= period
  while True:
    call_url_args = (url, timeout, period, regexp, pre_kafka_queue,)
    call = Process(target=call_url, args=call_url_args)
    wait = Process(target=time.sleep, args=(period,))
    call.start()
    wait.start()

    call.join()
    wait.join()
