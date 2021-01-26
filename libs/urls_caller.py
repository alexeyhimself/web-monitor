import sys
import time
import requests
from multiprocessing import Process

DEFAULT_TIMEOUT = 10  # time to wait request response [seconds]
DEFAULT_PERIOD = 60  # time between two consecutive requests [seconds]


def call_url(url, timeout):
  try:
    r = requests.get(url, timeout=timeout)
    msg = url + ': ' + str(r.status_code)
    print(msg)

  except requests.exceptions.ConnectionError:
    msg = url + ': ' + "ConnectionError"
    print(msg)
  except requests.exceptions.Timeout:
    msg = url + ': ' + "Timeout"
    print(msg)
  except Exception as why:
    msg = url + ': ' + str(why)
    print(msg)


def monitor_url(each_url):
  url = each_url.get("url")
  period = each_url.get("period", DEFAULT_PERIOD)
  timeout = each_url.get("timeout", DEFAULT_TIMEOUT)

  validate_period_and_timeout(period, timeout)

  while True:
    proc = Process(target=call_url, args=(url, timeout,))
    proc.start()
    proc.join()
    
    time.sleep(period)


def validate_period_and_timeout(period, timeout):
  if timeout > period:
    msg = "Timeout can't be greater than period. "
    msg += "But for %s it is: %s > %s" % (url, timeout, period)
    print(msg)
    sys.exit()
