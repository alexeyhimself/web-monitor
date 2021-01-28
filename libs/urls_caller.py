import re
import sys
import time, datetime
import requests

import logging
logger = logging.getLogger(__name__)

from multiprocessing import Process
from libs.config_loader import DEFAULT_TIMEOUT, DEFAULT_PERIOD


# Calls specified URL with defined parameters, forms JSON report and
# puts that report to pre-Kafka queue. In case of unrecoverable failure
# sys.exit()'s
def call_url(url, timeout, period, regexp, pre_kafka_queue):
  report = {
    'url': url,
    'timeout': timeout,
    'period': period,
    'regexp': regexp
  }

  try:
    time_start = time.time()

    # time must be prior of requests call to be in report in case of failure
    t = datetime.datetime.fromtimestamp(time_start)
    report.update({
      'time': t.strftime("%Y/%m/%d %H:%M:%S"),  # human readable
      'time_unix': time_start,  # for programs and db's
    })

    r = requests.get(url, timeout=timeout)
    time_end = time.time()

    # if OS time sync will happen during request and will be corrected back
    # then diff may become < 0! Many if's but may happen in long time use.
    response_time = round(time_end - time_start, 3)

    # overall result to look at, aggregates: 
    # response_code + transport issues + regexp
    result = 'ok' if r.status_code == 200 else 'fail'

    
    report.update({
      'transport': 'connected',
      'result': result,
      'response_time': response_time,
      'response_code': r.status_code
    })    

    # If HTTP 200 OK and regexp was assigned, then search for regexp and 
    # redefine result based on that search.
    if regexp and r.status_code == 200:
      regexp_found = True if re.search(regexp, r.text) else False
      result = 'ok' if regexp_found == True else 'fail'

      report.update({
        'regexp_found': regexp_found,
        'result': result
      })

  except requests.exceptions.ConnectionError:
    report.update({'transport': 'conn_error', 'result': 'fail'})
  except requests.exceptions.Timeout:
    report.update({'transport': 'conn_timeout', 'result': 'fail'})
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
