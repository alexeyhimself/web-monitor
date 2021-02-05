import time
import pytest
from tests.conftest import get_cfg_part, form_post_kafka_reports

from libs.kafka_receiver import init_kafka_consumer, check_queue_and_send_to_db


@pytest.mark.skip(reason="In CI need a Kafka server to test this.")
def test_kafka_consumer_inits_when_valid_config():
  kafka_cfg = get_cfg_part('kafka_pytest')
  consumer, topic = init_kafka_consumer(kafka_cfg)
  assert 1 == 1


def test_kafka_consumer_sys_exits_when_invalid_config():
  kafka_cfg = {}
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    consumer, topic = init_kafka_consumer(kafka_cfg)
  assert pytest_wrapped_e.type == SystemExit


class KafkaConsumerMock:
  def __init__(self, reports=None):
    if reports:
      self.reports = {'key': reports}
    else:
      self.reports = {}

  def poll(self, **kwargs):
    time.sleep(1)
    return self.reports

  def commit(self):
    pass

class KafkaConsumerMockWithoutPoll:  # causes an error in code when .poll()
  def __init__(self):
    pass


import signal
import psycopg2


def test_check_queue_and_send_to_db_works():
  cfg = {}
  topic = 'test'
  consumer = KafkaConsumerMock(form_post_kafka_reports())
  consumer.poll(timeout=1000)

  signal.signal(signal.SIGALRM, exit)
  signal.alarm(3)  # not marked as slow because normally will not wait for 3s

  with pytest.raises(Exception) as pytest_wrapped_e:
    check_queue_and_send_to_db(consumer, topic, cfg)
  assert pytest_wrapped_e.type == psycopg2.OperationalError

  signal.alarm(0)


@pytest.mark.slow  # marked as slow because of 3 seconds wait
def test_check_empty_queue_works():
  cfg = {}
  topic = 'test'
  consumer = KafkaConsumerMock()

  signal.signal(signal.SIGALRM, exit)
  signal.alarm(3)  # not marked as slow because normally will not wait for 3s

  with pytest.raises(Exception) as pytest_wrapped_e:
    check_queue_and_send_to_db(consumer, topic, cfg)
  assert pytest_wrapped_e.type == TypeError

  signal.alarm(0)


@pytest.mark.d
def test_check_queue_and_send_to_db_exits_on_exception():
  cfg = {}
  topic = 'test'
  consumer = KafkaConsumerMockWithoutPoll()

  signal.signal(signal.SIGALRM, exit)
  signal.alarm(5)  # not marked as slow because normally will not wait for 5s

  with pytest.raises(Exception) as pytest_wrapped_e:
    check_queue_and_send_to_db(consumer, topic, cfg)
  assert pytest_wrapped_e.type == AttributeError

  signal.alarm(0)
