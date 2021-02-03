import pytest
from libs.config_loader import validate_cfg, load_config


invalid_cfgs = [
	None,  # a very special one
	0,  # a special one
	1,  # not a JSON
	{},  # empty JSON
	# not an empty JSON, but has no mandatory keys 
	# (monitored_urls and kafka, db and kafka):
	{"abc": True},
	# mandatory keys exist, but value is empty list:
	{"kafka": {"abc": True}},
    {"mode": {"abc": True}},
	{"mode": "abc", "monitored_urls": [], "kafka": {"abc": True}},
	{"mode": "abc", "monitored_urls": [{"abc": True}], "kafka": {}},
	{"mode": "abc", "db": {"abc": True}, "kafka": {}},
	{"mode": "abc", "db": {}, "kafka": {"abc": True}},
	# mandatory keys exist, values are not empty, but do not contain 
	# mandatory keys (url, etc.):
	{"monitored_urls": [{"abc": True}], "kafka": {"abc": True}, "mode": "abc"}
]
@pytest.mark.parametrize("cfg", invalid_cfgs)
def test_sys_exits_on_invalid_cfg(cfg):
  # For this piece of code I used code from an article "Testing sys.exit() with pytest":
	# https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    validate_cfg(cfg)
  assert pytest_wrapped_e.type == SystemExit


def test_loads_valid_monitor_config():
	cfg = {
		"monitored_urls": [{"url": "string"}], 
		"kafka": {"any": "not empty"}, 
		"mode": "abc"
	}
	validate_cfg(cfg)
	assert 1 == 1


def test_load_config_without_path_param():
	cfg = load_config()
	assert isinstance(cfg, dict) == True


invalid_cfgs_paths = [
	None,  # a very special one
	0,  # a special one
	1,  # not a string
	"path/not/exists",
	"tests/test_validate_cfg.py",  # path exists, but content is not json
]
@pytest.mark.parametrize("cfg_path", invalid_cfgs_paths)
def test_load_config_with_invalid_path_param(cfg_path):
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    load_config(cfg_path)
  assert pytest_wrapped_e.type == SystemExit


# used https://docs.pytest.org/en/stable/tmpdir.html approach
def test_load_config_with_valid_path_param(tmp_path):
  cp = tmp_path / "config.json"
  cp.write_text('{}')
  cfg = load_config(cp)
  assert isinstance(cfg, dict) == True


@pytest.mark.parametrize("timeout", [None, "1.5", "1", "0"])
def test_sys_exits_if_url_timeout_is_not_a_number(timeout):
  cfg = {"monitored_urls": [{"url": "abc", "timeout": timeout}], 
         "kafka": {"abc": True}, "mode": "abc"}
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    validate_cfg(cfg)
  assert pytest_wrapped_e.type == SystemExit


@pytest.mark.parametrize("period", [None, "1.5", "1", "0"])
def test_sys_exits_if_url_period_is_not_a_number(period):
  cfg = {"monitored_urls": [{"url": "abc", "period": period}], 
         "kafka": {"abc": True}, "mode": "abc"}
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    validate_cfg(cfg)
  assert pytest_wrapped_e.type == SystemExit


@pytest.mark.parametrize("period", [None, "1.5", "1", "0"])
def test_sys_exits_if_timeout_greater_than_period(period):
  cfg = {"monitored_urls": [{"url": "abc", "period": 10, "timeout": 20}], 
         "kafka": {"abc": True}, "mode": "abc"}
  with pytest.raises(SystemExit) as pytest_wrapped_e:
    validate_cfg(cfg)
  assert pytest_wrapped_e.type == SystemExit
