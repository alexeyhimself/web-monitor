import re
import sys
import time, datetime
import requests

import logging
logger = logging.getLogger(__name__)

from multiprocessing import Process

DEFAULT_TIMEOUT = 10  # time to wait request response [seconds]
DEFAULT_PERIOD = 60  # time between two consecutive requests [seconds]


def call_url(url, timeout, period, regexp, pre_kafka_queue):
  report = {
    'url': url,
    'timeout': timeout,
    'period': period,
    'regexp': regexp
  }

  try:
    time_start = time.time()
    t = datetime.datetime.fromtimestamp(time_start)
    report['time'] = t.strftime("%Y/%m/%d %H:%M:%S")

    r = requests.get(url, timeout=timeout)
    time_end = time.time()

    report['transport'] = 'connected'

    response_time = round(time_end - time_start, 3)  # if OS time sync, mbe < 0
    report['response_time'] = response_time

    report['response_code'] = r.status_code
    report['result'] = 'ok' if r.status_code == 200 else 'fail'

    if regexp:  # allowed to search in non-200 OK pages too and redefine result
      regexp_found = True if re.search(regexp, r.text) else False
      report['regexp_found'] = regexp_found
      report['result'] = 'ok' if regexp_found == True else 'fail'

  except requests.exceptions.ConnectionError:
    report.update({'transport': 'conn_error', 'result': 'fail'})
  except requests.exceptions.Timeout:
    report.update({'transport': 'conn_timeout', 'result': 'fail'})
  except Exception as why:
    msg = url + ': ' + str(why)
    logger.error(msg, exc_info=True)
    sys.exit()

  pre_kafka_queue.put(report)


def monitor_url(each_url, pre_kafka_queue):
  url = each_url.get("url")
  period = each_url.get("period", DEFAULT_PERIOD)
  timeout = each_url.get("timeout", DEFAULT_TIMEOUT)
  regexp = each_url.get("regexp")

  # timeout must not be greater than period
  validate_period_and_timeout(url, period, timeout)

  # call call_url and wait for a period
  while True:
    call_url_args = (url, timeout, period, regexp, pre_kafka_queue,)
    call = Process(target=call_url, args=call_url_args)
    wait = Process(target=time.sleep, args=(period,))
    call.start()
    wait.start()

    call.join()
    wait.join()


def validate_period_and_timeout(url, period, timeout):
  if timeout > period:
    msg = "Timeout can't be greater than period. "
    msg += "But for %s it is: %s > %s" % (url, timeout, period)
    logger.error(msg)
    sys.exit()
