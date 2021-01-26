from libs.config_loader import load_config
from libs.urls_caller import monitor_url

from multiprocessing import Process


if __name__ == '__main__':
  cfg = load_config()

  monitored_urls = cfg.get("monitored_urls", [])
  if monitored_urls:
    procs = []
    for each_url in monitored_urls:
      proc = Process(target=monitor_url, args=(each_url,))
      procs.append(proc)
      proc.start()

    for proc in procs:
      proc.join()

  else:
    print("URL(s) to monitor have not been provided in config")
