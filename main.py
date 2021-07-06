import os
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
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
        break


def automate(url, company_id, product_id, id):
    review_data, gpt3_data, price, product_images = run_scrapping(url)
    run_models(review_data, gpt3_data, company_id, product_id, id, price, product_images)


if __name__ == "__main__":
    main()
