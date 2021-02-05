import pytest
from tests.conftest import get_cfg_part, form_pre_kafka_queue
from multiprocessing import JoinableQueue

from libs.kafka_sender import dump_queue, init_kafka_producer
from libs.kafka_sender import check_queue_and_send_to_kafka


@pytest.mark.skip(reason="In CI need a Kafka server to test this.")
def test_kafka_producer_inits_when_valid_config():
  kafka_cfg = get_cfg_part('kafka_pytest')
  producer, topic = init_kafka_producer(kafka_cfg)
  assert 1 == 1


def test_kafka_producer_sys_exits_when_invalid_config():
  kafka_cfg = {}
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    producer, topic = init_kafka_producer(kafka_cfg)
  assert pytest_wrapped_e.type == SystemExit


def test_dump_queue_works():
  pre_kafka_queue, report = form_pre_kafka_queue()
  dumped_queue = dump_queue(pre_kafka_queue)
  assert len(dumped_queue) == 1
  assert dumped_queue[0] == report


class KafkaProducerMock:
  def send(self, b, c):
    pass
  def flush(self):
    pass

class KafkaProducerMockWithoutFlush:  # causes an error in code when .flush()
  def send(self, b, c):
    pass


import signal


@pytest.mark.slow  # marked as slow because of 3 seconds wait
def test_check_queue_and_send_to_kafka_works():
  pre_kafka_queue, report = form_pre_kafka_queue()
  topic = 'test'
  producer = KafkaProducerMock()

  signal.signal(signal.SIGALRM, exit)
  signal.alarm(3)

  with pytest.raises(Exception) as pytest_wrapped_e:
    check_queue_and_send_to_kafka(producer, topic, pre_kafka_queue)
  assert pytest_wrapped_e.type == TypeError

  signal.alarm(0)


def test_check_queue_and_send_to_kafka_exits_on_exception():
  pre_kafka_queue, report = form_pre_kafka_queue()
  topic = 'test'
  producer = KafkaProducerMockWithoutFlush()

  signal.signal(signal.SIGALRM, exit)
  signal.alarm(3)  # not marked as slow because normally will not wait for 3s

  with pytest.raises(Exception) as pytest_wrapped_e:
    check_queue_and_send_to_kafka(producer, topic, pre_kafka_queue)
  assert pytest_wrapped_e.type == AttributeError

  signal.alarm(0)
