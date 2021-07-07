from crontab import CronTab
cron = CronTab(user='username')
job1 = cron.new(command='python3 main.py')
job1.minute.every(30)

for item in cron:
    print(item)
job.clear()

for item in cron:
    print(item)
cron.write()