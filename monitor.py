import sys
import requests

url = sys.argv[1]
if url:
  try:
    r = requests.get(url, timeout=10)
    print(r.status_code)

  except requests.exceptions.ConnectionError:
    print("ConnectionError")
  except requests.exceptions.Timeout:
    print("Timeout")
  except Exception as why:
    print(why)

else:
  print("URL not provided")
