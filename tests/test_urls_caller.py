import pytest
from libs.urls_caller import call_url, monitor_url

from multiprocessing import JoinableQueue


invalid_urls = [
	None,  # a very special one
	"",
  "http://",
  "https://"
]
@pytest.mark.parametrize("url", invalid_urls)
def test_sys_exits_on_invalid_url(url):
  pre_kafka_queue = JoinableQueue()

  # For this piece of code I used code from an article "Testing sys.exit() with pytest":
	# https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    call_url(url, 1, 10, None, pre_kafka_queue)
  assert pytest_wrapped_e.type == SystemExit


unavailable_urls = [
  "http://a",
  "https://ljnlkjhkjlhpiuyu896ohuih87t6798.no"
]
@pytest.mark.slow
@pytest.mark.parametrize("url", unavailable_urls)
def test_conn_error_on_unavailable_url(url):
  pre_kafka_queue = JoinableQueue()
  call_url(url, 1, 10, None, pre_kafka_queue)
  report = pre_kafka_queue.get()

  assert report.get('transport') == 'conn_error'
  assert report.get('is_fine') == False


def test_conn_timeout_on_url():
  pre_kafka_queue = JoinableQueue()
  # Used https://requests.readthedocs.io/en/master/user/advanced/#timeouts
  # to set timeout as a tuple: (connect timeout, read timeout)
  # and to get "read timeout" error
  call_url("http://google.com", (5, 0.000001), 10, None, pre_kafka_queue)
  report = pre_kafka_queue.get()

  assert report.get('transport') == 'conn_timeout'
  assert report.get('is_fine') == False
