from threading import Thread
import time
from reviews import run_scrapping
from models import run_models
from get_api import get_products
from api import send_data


def main():
    threads = []
    products = get_products()
    print(products)
    for product in products:
        automate(product['url'], product['company_id'], product['product_id'], product['id'])
        #thread = Thread(target=automate, args=(product['url'], product['company_id'], product['product_id'], product['id']))
        #threads.append(thread)
        #thread.start()
        #time.sleep(60)
    #for t in threads:
     #   t.join()  # joins all started threads to find working ups


def automate(url, company_id, product_id, id):
    review_data, gpt3_data = run_scrapping(url)
    run_models(review_data, gpt3_data, company_id, product_id, id)


if __name__ == "__main__":
    main()
