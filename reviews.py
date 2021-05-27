import csv
import random
import time
from collections import OrderedDict
from itertools import cycle
from threading import Thread
import requests
from dateutil import parser as dateparser
from lxml.html import fromstring
from selectorlib import Extractor
import multiprocessing.dummy as mp

total_pages_scrapped = 0


def run_everything(all_pages):
    working_ip = []
    num_of_loops = int(all_pages / 10)
    tens = 1

    def get_proxies():
        url3 = 'https://free-proxy-list.net/'
        response = requests.get(url3)
        parser = fromstring(response.text)
        print(parser.xpath('//tbody/tr'))
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:50]:
            print(i.xpath('.//td[7][contains(text(),"yes")]'))
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
                print(proxies)
        return proxies

    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    url4 = 'https://httpbin.org/ip'
    print('Finding viable ip address for proxy...')
    for i in range(1, 5):
        # Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d" % i)
        try:
            response = requests.get(url4, proxies={"http": proxy, "https": proxy})
            print(response.json())
            print(proxy)
            working_ip.append(proxy)
        except:
            # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
            # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
            print("Skipping. Connnection error")

    if all_pages < 10:
        print('@@@@ less then 10 pages @@@@')
        collect_data(1, all_pages, working_ip)
    else:
        print('@@@@ more then 10 pages @@@@')
        i = 1
        while i <= num_of_loops:
            time.sleep(1)
            print("current loop " + str(i))
            thread = Thread(target=collect_data, args=(tens, i * 10, working_ip))
            tens = tens + 10
            i = i + 1
            thread.daemon = True
            thread.start()
            thread.join()
        else:
            tens = tens + 10
            Thread(target=collect_data, args=(tens, all_pages, working_ip)).start()


def collect_data(lower_page, higher_page, working_ip):
    pages = higher_page

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

    def scrape(url2, ip_index):
        randint = ip_index
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
            print('current proxy ' + working_ip[randint])
            stop_count = 0
            r = ''
            while r == '':
                try:
                    r = requests.get(url2, headers=headers,
                                     proxies={"http": working_ip[randint], "https": working_ip[randint]})
                    break
                except:
                    sleep_time = random.randint(4, 5)
                    print("Connection refused by the server..")
                    print("Let me sleep for " + str(sleep_time) + " seconds")
                    print("ZZzzzz...")
                    time.sleep(sleep_time)
                    print("Was a nice sleep, now let me continue...")
                    stop_count = stop_count + 1
                    print("stop count " + str(stop_count))
                    if stop_count > 5:
                        randint = random.randint(0, len(working_ip) - 1)
                        print('to many stops, reassigning randint')
                        stop_count = 0
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

    with open("urls.txt", 'r') as urllist, open('data.csv', 'w', encoding='utf-8') as outfile, \
            open('gpt3training.txt', 'w', encoding='utf-8') as gptoutfile:
        writer = csv.DictWriter(outfile,
                                fieldnames=["title", "content", "date", "variant", "images", "verified", "author",
                                            "rating",
                                            "product", "url"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for url in urllist.readlines():
            for i in range(lower_page, pages):
                new_randint = random.randint(0, len(working_ip) - 1)
                data = scrape(url.rstrip() + str(i), new_randint)
                # sleep(random.randint(1, 2))
                print(data)
                while data['reviews'] is None:
                    print('Amazon blocked so scrapping again')
                    new_randint = random.randint(0, len(working_ip) - 1)
                    data = scrape(url.rstrip() + str(i), new_randint)
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
                    global total_pages_scrapped
                    total_pages_scrapped = total_pages_scrapped + 1
                    print("pages scrapped " + str(total_pages_scrapped))
                    # sleep(random.randint(1, 2))


# lower page has to start at 1
all_pages = 50

if __name__ == '__main__':
    run_everything(20)
