from libs.config_loader import load_config
from libs.servers_caller import call_server


if __name__ == '__main__':
  cfg = load_config()

  monitored_urls = cfg.get("monitored_urls", [])
  if monitored_urls:
    for each_url in monitored_urls:
      call_server(each_url)

  else:
    print("URL(s) to monitor have not been provided in config")
