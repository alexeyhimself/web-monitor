Web-Monitor Service
===========================
A Python app that periodically checks availability of specified HTTP(S) URL(s), forms JSON reports on those monitoring results, puts those reports to Kafka, and polls Kafka to store those reports in PostgreSQL DBMS.

Service runs forever and checks specified URL(s) for their reply within specified timeout and with specified period. A few basic failover procedres implemented:
* producer uses multiprocessing.Queues to put monitoring reports there before sending them to Kafka. That's why, if Kafka service is unavailable for a while, it applies throtling mechanism of Kafka availability polling and continues to keep reports in Queue.
* consumer has Kafka polling failover mechanism: if Kafka becomes unavailable, it applies throtling mechanism of Kafka availability polling.
* consumer Kafka commit depends on DBMS commit: if DBMS due to any reason can't save polled Kafka reports, consumer does not commit to Kafka and applies throtling mechanism of DBMS availability polling.


# Getting Started
## Prerequisites
* Kafka service is up and running
* PostgreSQL service is up and running

## How to install
### Clone source code and install dependencies:
```
# get source code
git clone https://github.com/alexeyhimself/web-monitor.git

# init virtualenv
python3 -m venv ./web-monitor/
cd ./web-monitor/
source bin/activate

# install required python libs
pip3 install -r install/requirements.txt
```

### Create Kafka topic
Create Kafka `topic`.

### Create monitoring table in DB
Connect to PostgreSQL with your favorite client and apply SQL commands from `install/init_monitoring_db.sql` file.

### Update config.json
- Update `configs/config.json`, fill all the parameters for Kafka and Postgres:
```json
{
  "kafka": {
    "host": "",
    "port": "19071",
    "topic": "",
    "ssl_cafile": "certs/kafka/ca.pem",
    "ssl_certfile": "certs/kafka/service.cert",
    "ssl_keyfile": "certs/kafka/service.key"
  },
  "db": {
    "host": "",
    "port": "19069",
    "db_name": "",
    "user": "",
    "password": "",
    "sslmode": "require",
    "sslrootcert": "certs/db/ca.pem",
  }
}
```
- Update `configs/config.json`, change monitoring URL(s) to your server(s):
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

## Start monitoring server
In `web-monitor` folder run:
```
python3 monitor.py
```

## Logs
Service logs messages by default to `logs/monitor.log`. But it can log to console as well.

## Help for developers
If you create `.local_debug` file in `web-monitor` folder (it is already in .gitignore) then logs will be redirected from file to console. 
Logs will have INFO level if you add in `.local_debug` the following structure:
```
{
    "log_level": "INFO"
}
```
Extend this file for your needs.

## Autotests
To execute autotests in `web-monitor` folder run a command:
```
pytest
```

## License
WTFPL
