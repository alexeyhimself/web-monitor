from libs.local_debug_loader import load_local_debug

import json


def test_load_local_debug_file_exists(tmpdir):
  p = tmpdir.mkdir("pytest").join("local_debug_test")
  test_json = {'test': 'json'}
  p.write(json.dumps(test_json))
  test_file_path = str(p)
  ld_cfg = load_local_debug(test_file_path)

  assert ld_cfg == test_json


def test_load_local_debug_file_not_exist(tmpdir):
  p = tmpdir.mkdir("pytest").join("local_debug_test")
  test_file_path = str(p)
  ld_cfg = load_local_debug(test_file_path)

  assert ld_cfg == {}
