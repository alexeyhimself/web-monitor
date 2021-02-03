# .local_debug file that is in .gitignore that helps to distinguish:
# DEV or PRO machine and provides options for fast switching of configuration.
# For example, changing log_level (to see what PRO logs will look like to make) 
# them more comprehensive or add more log details when developing features 
# without changing this file. 
import os.path
from libs.config_loader import load_config
ld_path = '.local_debug'


def load_local_debug(ld_path = ld_path):
  if os.path.isfile(ld_path):
    return load_config(ld_path)
  else:
    return {}
