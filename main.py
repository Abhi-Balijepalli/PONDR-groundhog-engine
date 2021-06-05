# from models import run_models
from reviews import run_scrapping
from models import run_models
from get_api import get_products
from api import send_data


def main():
    products = get_products()
    print(products)
    for product in products:
        print(product)
        print(product['url'])
        review_data, gpt3_data = run_scrapping(product['url'])
        run_models(review_data, gpt3_data, product['company_id'], product['product_id'], product['id'])


if __name__ == "__main__":
    main()
