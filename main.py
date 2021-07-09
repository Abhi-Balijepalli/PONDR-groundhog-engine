import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0"
from threading import Thread
import time
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from reviews import run_scrapping
from models import run_models
from get_api import get_products
from api import send_data


def scheduler_run_forever():
    try:
        scheduler = BlockingScheduler()

        # Run every 15mins all day (Works!)
        # scheduler.add_job(main, 'interval', minutes=15)

        # Run every 15mins from 6:15am - 11:15pm a day job Method (Testing right now)
        scheduler.add_job(main, 'cron', hour='6-23', minutes='*/15', args=['enterprise-automation'])
        
        # Run once a day at 1am to 5am job Method (Needs to be tested)
        # scheduler.add_job(job, 'cron', hour='1-5', args=['amazon-deals'])
        scheduler.start()
    except:
        print('crashed :(')
        scheduler_run_forever()



def main(text):
    
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('{} --- {}'.format(text, t))

    threads = []
    products = get_products()
    print(products)
    for product in products:
        automate(product['url'], product['company_id'], product['product_id'], product['id'])
        break


def automate(url, company_id, product_id, id):
    review_data, gpt3_data, price, product_images = run_scrapping(url)
    run_models(review_data, gpt3_data, company_id, product_id, id, price, product_images)


if __name__ == "__main__":
    scheduler_run_forever()
