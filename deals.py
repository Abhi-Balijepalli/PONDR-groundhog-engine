from deals_get import get_deals_of_the_day
from deals_reviews import run_deals_scrapping
from deals_models import run_deals

if __name__ == "__main__":
    asin_list = get_deals_of_the_day('https://www.amazon.com/events/collegedeals?ref=deals_deals_deals-grid_slot-15_39f3_dt_dcell_img_2_024739bb')
    id = 0
    for asin in asin_list:
        review_data, gpt3_data, price, product_images, short_description, long_description, category = run_deals_scrapping(asin)
        run_deals(review_data, gpt3_data, id, price, product_images, short_description, long_description, category)
        id = id + 1
