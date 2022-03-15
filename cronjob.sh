# a sample bash script to run as a cronjob
# this will a) activate the venv, b) run the check-bins.py script, c) run the daily-monitor script
# use the following list of digits to run the script every day at 19:30
# 30 19 * * * . /path/to/cronjob.sh >/dev/null 2>&1

#!/bin/bash
cd /home/pi/projects/hackney-bin-bot
. venv/bin/activate
# python3 check-bins.py
python3 daily-monitor.py
deactivate
exit