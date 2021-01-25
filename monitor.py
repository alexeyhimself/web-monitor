import sys
import requests
import json

CONFIG_PATH = 'config.json'
DEFAULT_TIMEOUT = 10  # seconds

try:
  with open(CONFIG_PATH) as file:
    cfg_file = file.read()
  cfg = json.loads(cfg_file)

except Exception as why:
  err_msg = "Could not load config file due to an error: " + str(why)
  print(err_msg)
  sys.exit()

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
