import re
import sys
import time
import requests

import logging
logger = logging.getLogger(__name__)

from multiprocessing import Process

DEFAULT_TIMEOUT = 10  # time to wait request response [seconds]
DEFAULT_PERIOD = 60  # time between two consecutive requests [seconds]


def call_url(url, timeout, regexp):
  try:
    time_start = time.time()
    r = requests.get(url, timeout=timeout)
    time_end = time.time()

    request_time = round(time_end - time_start, 3)
    msg = url + ': ' + str(r.status_code) + ', time: %ss' % str(request_time)

    if regexp:
      regexp_found = True if re.search(regexp, r.text) else False
      msg += ', regexp found: %s' % str(regexp_found)

    logger.debug(msg)

  except requests.exceptions.ConnectionError:
    msg = url + ': ' + 'ConnectionError'
    logger.warning(msg)
  except requests.exceptions.Timeout:
    msg = url + ': ' + 'Timeout, >' + str(timeout) + 's'
    logger.warning(msg)
  except Exception as why:
    msg = url + ': ' + str(why)
    logger.error(msg)


def monitor_url(each_url):
  url = each_url.get("url")
  period = each_url.get("period", DEFAULT_PERIOD)
  timeout = each_url.get("timeout", DEFAULT_TIMEOUT)
  regexp = each_url.get("regexp")

  validate_period_and_timeout(url, period, timeout)

  while True:
    proc = Process(target=call_url, args=(url, timeout, regexp,))
    proc.start()
    proc.join()
    
    time.sleep(period)


def validate_period_and_timeout(url, period, timeout):
  if timeout > period:
    msg = "Timeout can't be greater than period. "
    msg += "But for %s it is: %s > %s" % (url, timeout, period)
    logger.error(msg)
    sys.exit()
