import requests

DEFAULT_TIMEOUT = 10  # time to wait request response [seconds]


def call_server(each_url):
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
