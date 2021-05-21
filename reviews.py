import csv
import random
from collections import OrderedDict
from time import sleep
import requests
from dateutil import parser as dateparser
from numpy import unicode
from selectorlib import Extractor
import time
from lxml.html import fromstring
import requests
from itertools import cycle
import traceback

pages = 32

# This data was created by using the curl method explained above
headers_list = [
    # Firefox 77 Mac
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Firefox 77 Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')


def scrape(url2):
    # Create ordered dict from Headers above
    global headers
    ordered_headers_list = []
    for headers in headers_list:
        h = OrderedDict()
        for header, value in headers.items():
            h[header] = value
        ordered_headers_list.append(h)
    for i in range(1, 4):
        # Pick a random browser headers
        headers = random.choice(headers_list)
        # Create a request session
        r = requests.Session()
        r.headers = headers
        # Download the page using requests
        print("Downloading %s" % url2)
        r = ''
        while r == '':
            try:
                r = requests.get(url2, headers=headers, proxies={"http": '61.37.223.152:8080', "https": '61.37.223.152:8080'})
                break
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue
        # Simple check to check if page was blocked (Usually 503)
        print(str(r.status_code))
        if r.status_code > 500:
            if "To discuss automated access to Amazon data please contact" in r.text:
                print("Page %s was blocked by Amazon. Please try using better proxies\n" % url2)
            else:
                print("Page %s must have been blocked by Amazon as the status code was %d" % (url2, r.status_code))
            return None
        # Pass the HTML of the page and create
        return e.extract(r.text)


def get_proxies():
    url3 = 'https://free-proxy-list.net/'
    response = requests.get(url3)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            return proxies

# If you are copy pasting proxy ips, put in the list below
# proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']
proxies = get_proxies()
proxy_pool = cycle(proxies)
url4 = 'https://httpbin.org/ip'
for i in range(1, 11):
# Get a proxy from the pool
    proxy = next(proxy_pool)
    print("Request #%d" % i)
    try:
        response = requests.get(url4, proxies={"http": proxy, "https": proxy})
        print(response.json())
        print(proxy)
    except:
        # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
        # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
        print("Skipping. Connnection error")


# product_data = []
with open("urls.txt", 'r') as urllist, open('data.csv', 'w', encoding='utf-8') as outfile, \
        open('gpt2training.txt', 'w', encoding='utf-8') as gptoutfile:
    writer = csv.DictWriter(outfile,
                            fieldnames=["title", "content", "date", "variant", "images", "verified", "author",
                                        "rating",
                                        "product", "url"], quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for url in urllist.readlines():
        for i in range(1, pages):
            data = scrape(url.rstrip() + str(i))  # goes through all the pages
            sleep(random.randint(1, 2))
            # print(data)
            if data:
                for r in data['reviews']:
                    r["product"] = data["product_title"]
                    r['url'] = url
                    if 'verified' in r:
                        if r['verified'] is None:
                            r['verified'] = 'No'
                        elif 'Verified Purchase' in r['verified']:  # not sure if nessesary
                            r['verified'] = 'Yes'
                        else:
                            r['verified'] = 'Yes'
                        if r['rating'] is None: r['rating'] = 'None'
                    r['rating'] = r['rating'].split(' out of')[0]
                    date_posted = r['date'].split('on ')[-1]
                    if r['images']:
                        r['images'] = "\n".join(r['images'])
                    r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
                    r['content'] = r['content'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
                    r['title'] = r['title'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
                    r['author'] = r['author'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
                    writer.writerow(r)
                    gptoutfile.write(r['content'])
                    gptoutfile.write("\n")
                    print(str(r))
                    # sleep(random.randint(1, 2))
