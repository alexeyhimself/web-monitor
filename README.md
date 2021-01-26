# Web-Monitor Service

## About
Python app that checks availability of specified HTTP service. It runs forever and checks specified URL(s) for reply within specified timeout and with specified period.
* If service is HTTP(S) available, then HTTP(S) response code will be printed to stdio.
* If service is HTTP(S) unavailable, then either ConnectionError or Timeout error will be printed to stdio.
* If any other error will occur, reason will be printed to stdio.

## How to install
Download installation file and run it:
```
wget -N https://raw.githubusercontent.com/alexeyhimself/web-monitor/main/install.sh && sh install.sh
```

## How to use
```
python3 monitor.py
```
adjust URL(s) of monitored service(s) and their optional parameters in `config.json`:
```json
{
  "monitored_urls": [
    {"url": "https://google.com"},
    {"url": "https://yandex.com", "timeout": 1},
    {"url": "https://bing.com", "period": 30}
  ]
}
```
Optional monitored URL(s) parameters are:
* `timeout` - time to wait request response [seconds], **default 10**
* `period` - time between two consecutive requests [seconds], **default 60**


## Run autotests
```
pytest
```

## License
WTFPL
