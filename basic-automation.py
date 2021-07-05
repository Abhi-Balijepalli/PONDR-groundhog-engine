import schedule
import sys
import time
from main import main

schedule.every().hour(6).do(main)

while True:
    # is pending to run or not
    schedule.run_pending(main)
    time.sleep(1)