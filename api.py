# importing the requests library
import requests
import json


def send_data(id):
    # Opening JSON file
    f = open('package_' + str(id) + '.json')

    # returns JSON object as
    # a dictionary
    package = json.load(f)

    # defining the api-endpoint
    API_ENDPOINT = "https://groundhog.letspondr.com/analyze"

    # data to be sent to api

    print(package)
    # sending post request and saving response as response object
    r = requests.post('https://groundhog.letspondr.com/analyze', json=package)

    # extracting response text
    pastebin_url = r.text

    print("The pastebin URL is:%s " % pastebin_url)
