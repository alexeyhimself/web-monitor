# exit on any command failure
set -e

# get source code
git clone https://github.com/alexeyhimself/web-monitor.git

# init virtualenv
python3 -m venv ./web-monitor/
cd ./web-monitor/
source bin/activate

# install required python libs
pip3 install -r requirements.txt
