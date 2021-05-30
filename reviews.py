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

total_pages_scrapped = 0
old_randints = [None]  # empty list for now, see end of run_everything() for more
csv_outfile = []
txt_outfile = []
working_ip = []
proxy_pool = []


def get_proxies():  # getting proxies by scrapping the site for free

    url3 = 'https://free-proxy-list.net/'
    response = requests.get(url3)
    parser = fromstring(response.text)
    print(parser.xpath('//tbody/tr'))
    proxies = set()

    for i in parser.xpath('//tbody/tr')[:150]:
        print(i.xpath('.//td[7][contains(text(),"yes")]'))
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            print(proxies)
    return proxies


def get_pro_proxies():  # getting proxies from the paid api
    proxies = set()
    url5 = 'http://list.didsoft.com/get?email=tomcs333@gmail.com&pass=9txsme&pid=http3000&showcountry=no'
    response = requests.get(url5)
    ip_string = response.text
    for proxy in ip_string.splitlines():
        print(proxy)
        proxies.add(proxy)
    return proxies


def find_ip(lower_range,
            upper_range):  # finds ip in a given range from an ip list generated from get_pro_proxie or get_proxie

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
            # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
            # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
            print("Skipping. Connnection error")


def run_everything(all_pages):
    global thread  # this is global for joining later
    global old_randints  # including old_randints as global
    global proxy_pool
    num_of_loops = int(all_pages / 5)  # how many loops/ threads are needed
    tens = 1  # the lower bound of the scrape() method
    old_randints = old_randints * num_of_loops  # making a list of size num_of_loops for proxy_index storage

    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    print('Finding viable ip address for proxy...')

    ip_threads = []  # lists of threads to join
    high_i = 2
    low_i = 1

    while low_i < 51:  # change number here for num ips checked
        ip_thread = Thread(target=find_ip, args=(low_i, high_i))
        ip_threads.append(ip_thread)
        ip_thread.start()
        low_i = low_i + 1
        high_i = high_i + 1
        time.sleep(0.1)

    for t in ip_threads:
        t.join()  # joins all started threads to find working ups

    scrape_threads = []

    if all_pages < 10:
        print('@@@@ less then 10 pages @@@@')
        collect_data(1, all_pages, all_pages, 1)
    else:
        print('@@@@ more then 10 pages @@@@')
        i = 1
        while i <= num_of_loops:
            time.sleep(1)
            old_randints[i - 1] = random.randint(0, len(working_ip) - 1)
            print("current loop " + str(i))
            thread = Thread(target=collect_data, args=(tens, (i * 5) + 1, all_pages, i))
            tens = tens + 5
            i = i + 1
            scrape_threads.append(thread)
            thread.start()

            # fix not 10s bug here!!

        for t in scrape_threads:
            t.join()

        with open('data.csv', 'w', encoding='utf-8') as outfile, open('gpt3training.txt', 'w',
                                                                      encoding='utf-8') as gptoutfile:
            writer = csv.DictWriter(outfile,
                                    fieldnames=["title", "content", "date", "variant", "images", "verified", "author",
                                                "rating",
                                                "product", "url"], quoting=csv.QUOTE_ALL)

            for row in csv_outfile:
                writer.writerow(row)

            for row in txt_outfile:
                gptoutfile.write(row)


def collect_data(lower_page, higher_page, all_pages, thread_number):
    # This data was created by using the curl method explained above
    headers_list = [
        # Firefox 77 Mac
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
        }
    ]

    # Create an Extractor by reading from the YAML file
    e = Extractor.from_yaml_file('selectors.yml')

    def scrape(url2, ip_index, thread_number):
        global old_randints
        global headers
        global csv_outfile
        global txt_outfile
        global working_ip

        randint = ip_index
        # Create ordered dict from Headers above
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
            site_response = requests.Session()
            site_response.headers = headers
            # Download the page using requests
            print("Downloading %s" % url2)
            print('current proxy ' + working_ip[randint])
            stop_count = 0
            r = ''
            while r == '':
                try:
                    r = site_response.get(url2, headers=headers,
                                          proxies={"http": working_ip[randint], "https": working_ip[randint]},
                                          timeout=45)
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
                    if stop_count > 4:
                        randint = random.randint(0, len(working_ip) - 1)  # try to assign this to the global ip array
                        old_randints[thread_number - 1] = randint
                        # print('to many stops, reassigning randint')
                        stop_count = 0
                    continue
            # Simple check to check if page was blocked (Usually 503)
            print(str(r.status_code))
            return e.extract(r.text)

    with open("urls.txt", 'r') as urllist:
        # writer.writeheader()
        for url in urllist.readlines():
            for i in range(lower_page, higher_page):
                data = scrape(url.rstrip() + str(i),
                              old_randints[thread_number - 1],
                              thread_number)  # appends the page number to the end of the url
                # sleep(random.randint(1, 2))
                print(data)
                while data['reviews'] is None:
                    print('Amazon blocked so scrapping again')
                    print(old_randints[thread_number - 1])
                    print('ip deleting ' + working_ip[old_randints[thread_number - 1]])
                    del working_ip[old_randints[thread_number - 1]]
                    if len(working_ip) < 5:
                        ip_threads = []  # lists of threads to join
                        high_i = 2
                        low_i = 1
                        while low_i < 26:  # change number here for num ips checked
                            ip_thread = Thread(target=find_ip, args=(low_i, high_i))
                            ip_threads.append(ip_thread)
                            ip_thread.start()
                            low_i = low_i + 1
                            high_i = high_i + 1
                            time.sleep(0.1)

                        for t in ip_threads:
                            t.join()  # joins all started threads to find working ups

                    old_randints[thread_number - 1] = random.randint(0, len(working_ip) - 1)
                    data = scrape(url.rstrip() + str(i), old_randints[thread_number - 1], thread_number)
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
                        # writer.writerow(r)
                        csv_outfile.append(r)
                        # gptoutfile.write(r['content'] + "\n")
                        txt_outfile.append(r['content'] + "\n")
                        print(str(r))
                    global total_pages_scrapped
                    total_pages_scrapped = total_pages_scrapped + 1
                    print(str(round((total_pages_scrapped / all_pages) * 100, 2)) + "%")
                    # sleep(random.randint(1, 2))


# lower page has to start at 1

if __name__ == '__main__':
    run_everything(40)
