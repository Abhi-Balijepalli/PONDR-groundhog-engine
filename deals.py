from deals_get import get_deals_of_the_day
from deals_reviews import run_deals_scrapping
from deals_models import run_deals
import requests
import json
from threading import Thread
import sys
import time


def do_everything(id, asin, type):
    review_data, gpt3_data, price, product_images, short_description, long_description, category = run_deals_scrapping(
        asin, id)
    if review_data is None:
        print("No reviews, skipped")
        sys.exit()

    run_deals(review_data, gpt3_data, id, price, product_images, short_description, long_description, category, asin,
              type)


if __name__ == "__main__":
    first_page = int(input('first page? '))
    last_page = int(input('last page? '))
    type = input('type ')

    for i in range(first_page, last_page + 1):
        link = "https://www.amazon.com/gp/goldbox/?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A" + str(i*60) + "%252C%2522presetId%2522%253A%2522E0CC976FC92938FBCE3AED450B499476%2522%252C%2522sorting%2522%253A%2522BY_CUSTOM_CRITERION%2522%257D"
        asin_list = get_deals_of_the_day(link)
        r = requests.get('https://groundhog.letspondr.com/asins')
        old_asin_list = json.loads(r.text)
        print(old_asin_list['IDs'])
        print(asin_list)
        final_asin_list = []
        for raw_asin in asin_list:
            if raw_asin not in old_asin_list['IDs']:
                final_asin_list.append(raw_asin)

        print(final_asin_list)

        id = 0
        deals_threads = []
        for asin in final_asin_list:
            print('Starting thread number ' + str(id))
            deals_thread = Thread(target=do_everything, args=(id, asin, type))
            deals_threads.append(deals_thread)
            deals_thread.start()
            time.sleep(1)
            id = id + 1

        print('@@@@@@@@@@ Joining Threads @@@@@@@@@@')
        for t in deals_threads:
            t.join()
        deals_thread = []
