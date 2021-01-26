import sys
import time
import requests
from multiprocessing import Process

DEFAULT_TIMEOUT = 10  # time to wait request response [seconds]
DEFAULT_PERIOD = 60  # time between two consecutive requests [seconds]


def call_url(each_url):
  url = each_url.get("url")
  timeout = each_url.get("timeout", DEFAULT_TIMEOUT)

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


def wait_till_next_call(each_url):
  period = each_url.get("period", DEFAULT_PERIOD)
  time.sleep(period)


def async_call(proc):
  proc.start()
  proc.join()


def monitor_url(each_url):
  validate_period_and_timeout(each_url)

  while True:
    async_call(Process(target=call_url, args=(each_url,)))
    async_call(Process(target=wait_till_next_call, args=(each_url,)))


def validate_period_and_timeout(each_url):
  url = each_url.get("url")
  period = each_url.get("period", DEFAULT_PERIOD)
  timeout = each_url.get("timeout", DEFAULT_TIMEOUT)
  if timeout > period:
    msg = "Timeout (%s) can't be greater than period (%s). " % (timeout, period)
    msg += "But for %s it is." % url
    print(msg)
    sys.exit()
