import requests
from libs.config_loader import load_config

DEFAULT_TIMEOUT = 10  # seconds

cfg = load_config()

monitored_urls = cfg.get("monitored_urls", [])
if monitored_urls:
  for each_url in monitored_urls:
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
      msg = url + ': ' + "ConnectionError"
      print(msg)
    except Exception as why:
      msg = url + ': ' + str(why)
      print(msg)

else:
  print("URL(s) to monitor have not been provided in config")
