import random
import re
import time
from itertools import cycle
from threading import Thread
import requests
from lxml.html import fromstring
import json

working_ip = []
proxy_pool = []


def get_proxies():  # getting proxies by scrapping the site for free
    url3 = 'https://free-proxy-list.net/'
    response = requests.get(url3)
    parser = fromstring(response.text)
    print(parser.xpath('//tbody/tr'))
    proxies = set()

    for i in parser.xpath('//tbody/tr')[:200]:
        print(i.xpath('.//td[7][contains(text(),"yes")]'))
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            print(proxies)
    return proxies


def find_ip(lower_range, upper_range):
    # finds ip in a given range from an ip list generated from get_pro_proxie or get_proxie
    url4 = 'https://httpbin.org/ip'
    session = requests.Session()
    for i in range(lower_range, upper_range):
        # Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d" % i)
        try:
            response = session.get(url4, proxies={"http": proxy, "https": proxy}, timeout=10)
            print(response.json())
            print(proxy)
            working_ip.append(proxy)
        except:
            # Most free proxies will often get connection errors. You will have retry the entire request using
            # another proxy to work. We will just skip retries as its beyond the scope of this tutorial and we are
            # only downloading a single url
            print("Skipping. Connnection error")


def get_deals_of_the_day(front_url):
    print("@@@@@@ getting deals of the day page @@@@@@")

    product_headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        # Firefox 77 Windows
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        # Chrome 83 Mac
        {
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        },
        # Chrome 83 Windows
        {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }]
    # Create a request session
    site_response = requests.Session()
    # Download the page using requests
    print("Downloading %s" % front_url)
    current_ip = random.randint(0, len(working_ip) - 1)
    print('current proxy ' + working_ip[current_ip])
    stop_count = 0
    headers = random.choice(product_headers)
    r = ''
    while r == '':
        try:
            r = site_response.get(front_url, headers=headers, proxies={"http": working_ip[current_ip],
                                                                       "https": working_ip[current_ip]})
            response = str(r.text)
            if "assets.mountWidget(" not in response:
                print('Amazon blocked so new ip')
                print(r.text)
                current_ip = random.randint(0, len(working_ip) - 1)
                headers = random.choice(product_headers)
                r = ''
            else:
                break

        except:
            sleep_time = 5
            print("Connection refused by the server..")
            print("Let me sleep for " + str(sleep_time) + " seconds")
            print("ZZzzzz...")
            time.sleep(sleep_time)
            print("Was a nice sleep, now let me continue...")
            stop_count = stop_count + 1
            print("stop count " + str(stop_count))
            if stop_count > 3:
                current_ip = random.randint(0, len(working_ip) - 1)  # try to assign this to the global ip array
                print('to many stops, reassigning randint')
                stop_count = 0
            continue
    response = str(r.text)

    result = re.search('assets.mountWidget(.*)"enableDealStatusUpdates":true}', response)

    final_JSON = result.group(1)
    final_JSON = final_JSON[:-1]
    final_JSON = final_JSON + '}'
    final_JSON = final_JSON[11:]
    final_JSON_object = json.loads(final_JSON)

    test_json = final_JSON_object['prefetchedData']
    test_json = test_json['dcsGetDealsList']
    dealDetails = test_json[0]
    dealDetails = dealDetails['dealDetails']
    for key_object in dealDetails:
        individual_deal = dealDetails[key_object]
        if 'reviewAsin' in individual_deal:
            print(individual_deal['reviewAsin'])
        else:
            print(individual_deal)


def main():
    global proxy_pool

    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    print('Finding viable ip address for proxy...')

    ip_threads = []  # lists of threads to join
    high_i = 2
    low_i = 1

    while low_i < 76:  # change number here for num ips checked
        ip_thread = Thread(target=find_ip, args=(low_i, high_i))
        ip_threads.append(ip_thread)
        ip_thread.start()
        low_i = low_i + 1
        high_i = high_i + 1
        time.sleep(0.1)

    for t in ip_threads:
        t.join()  # joins all started threads to find working ups

    get_deals_of_the_day('https://www.amazon.com/gp/goldbox/')
    #'https://www.amazon.com/events/collegedeals?ref=deals_deals_deals-grid_slot-15_39f3_dt_dcell_img_2_024739bb' for college deals of the day
    # https://www.amazon.com/gp/goldbox/
    # https://www.amazon.com/events/schooldeals

if __name__ == "__main__":
    main()
