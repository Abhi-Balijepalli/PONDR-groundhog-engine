import schedule
import sys
import os
import time
from main import main

schedule.every(6).hours.do(main)

while True:
    # is pending to run or not
    schedule.run_pending(main)
    time.sleep(1)