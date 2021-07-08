# from crontab import CronTab
# cron = CronTab(user='username')
# job1 = cron.new(command='python3 main.py')
# job1.minute.every(30)

# for item in cron:
#     print(item)
# job.clear()

# for item in cron:
#     print(item)
# cron.write()
import os
import sys
from main import main
from apscheduler.schedulers.blocking import BlockingScheduler

def some_job():
    return main()

scheduler = BlockingScheduler()
scheduler.add_job(some_job, 'interval', minutes=28)
scheduler.start()
