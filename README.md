# Web-Monitor Service

## About
Python app that checks availability of specified HTTP service. It runs forever and checks specified URL(s) for reply within specified timeout and with specified period.
* If service is HTTP(S) available, then HTTP(S) response code will be printed to stdio.
* If service is HTTP(S) unavailable, then either ConnectionError or Timeout error will be printed to stdio.
* If any other error will occur, reason will be printed to stdio.

## How to install
Download installation file and run it:
```
wget -N https://raw.githubusercontent.com/alexeyhimself/web-monitor/main/install/install.sh && sh install.sh
```

## How to use
In `web-monitor` folder run:
```
python3 monitor.py
```
This will start monitoring of "https://google.com" with the period of 60 seconds.
To set your own URL(s) of monitored service(s) and their optional parameters, adjust `config.json` file:
```json
{
  "monitored_urls": [
    {"url": "https://google.com"},
    {"url": "https://yandex.ru", "timeout": 1},
    {"url": "https://bing.com", "timeout": 10, "period": 30}
  ]
}
```
Mandatory parameter - is `url`. Other parameters are optional:
* `timeout` [seconds], default: 10 - maximum time to wait request's response. If exceeded then request is considered as failed due to timeout;
* `period` [seconds], default: 60 - time between two consecutive monitoring requests. Must be greater than `timeout`.


## Run autotests
In `web-monitor` folder run:
```
pytest
```

## License
WTFPL
