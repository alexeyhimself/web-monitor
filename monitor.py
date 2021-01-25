import sys
import requests

url = sys.argv[1]
if url:
  r = requests.get(url)
  print(r.status_code)
else:
  print("URL not provided")
