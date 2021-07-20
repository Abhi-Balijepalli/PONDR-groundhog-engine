from deals_get import get_deals_of_the_day
from deals_reviews import run_deals_scrapping
from deals_models import run_deals
import requests
import json

if __name__ == "__main__":

    asin_list = get_deals_of_the_day('https://www.amazon.com/events/collegedeals?ref=deals_deals_deals-grid_slot-15_39f3_dt_dcell_img_2_024739bb')
    r = requests.get('https://groundhog.letspondr.com/asins')
    old_asin_list = json.loads(r.text)
    final_asin_list = list(set(asin_list + old_asin_list['IDs']))
    print(final_asin_list)
    id = 0
    for asin in final_asin_list:
        review_data, gpt3_data, price, product_images, short_description, long_description, category = run_deals_scrapping(asin)
        if review_data is None:
            print("No reviews, skipped")
            continue
            
        run_deals(review_data, gpt3_data, id, price, product_images, short_description, long_description, category, asin)
        id = id + 1
