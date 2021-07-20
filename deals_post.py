# importing the requests library
import requests
import json


def send_deals_data(id):
    # Opening JSON file
    f = open('package_' + str(id) + '.json')

    # returns JSON object as
    # a dictionary
    package = json.load(f)

    # data to be sent to api

    print(package)
    # sending post request and saving response as response object
    r = requests.post('https://groundhog.letspondr.com/consumer_product', json=package)

    # extracting response text
    pastebin_url = r.text

    print("The pastebin URL is:%s " % pastebin_url)
