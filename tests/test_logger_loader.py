try:
  from libs.logger_loader import *
  loaded = True
except Exception:
  loaded = False


def test_logger_loader_loads():
  assert loaded == True
