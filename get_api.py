# importing the requests library
import requests
import json
import csv


def get_products():
    # defining the api-endpoint
    API_ENDPOINT = "https://groundhog.letspondr.com/product/waitlist"

    # data to be sent to api

    # sending post request and saving response as response object
    r = requests.get(API_ENDPOINT)

    # extracting response text
    pastebin_url = r.text

    print("The pastebin URL is:%s" % pastebin_url)
    aList = json.loads(pastebin_url)
    r = {}
    api_dict = []
    i = 0
    for elem in aList["Products to be analyized"]:
        r['company_id'] = elem['Company_id']
        r['product_id'] = elem['Product_id']
        r['url'] = elem['Amazon_link']
        r['id'] = i
        i = i + 1
        api_dict.append(r)
    return api_dict
