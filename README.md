# web-monitor

## About
Python app that checks availability of specified HTTP service.
* If service is HTTP(S) available, then HTTP(S) response code will be printed to stdio.
* If service is HTTP(S) unavailable, then either ConnectionError or Timeout (more than 10s wait) error will be printed to stdio.
* If any other error will occur, reason will be printed to stdio.

## How to install
```
git clone https://github.com/alexeyhimself/web-monitor.git
python3 -m venv ./web-monitor/
source bin/activate
cd ./web-monitor/
pip3 install -r requirements.txt
```

## How to use
```
python3 monitor.py
```
adjust URL(s) of monitored service(s) in config.json
