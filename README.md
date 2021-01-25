# web-monitor

## About
Python app that checks availability of specified HTTP service.
If service is available, then HTTP response code will be printed to stdio. Otherwise exception will occur.

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
python3 monitor.py https://google.com
```
where "https://google.com" - is an URL of monitored service
