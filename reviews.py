import random
import re
import sys
import time
from collections import OrderedDict
from itertools import cycle
from threading import Thread
import requests
from dateutil import parser as dateparser
from lxml.html import fromstring
from selectorlib import Extractor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

total_pages_scrapped = 0
old_randints = [None]  # empty list for now, see end of run_scrapping() for more
csv_outfile = []
txt_outfile = []
working_ip = []
proxy_pool = []
scrape_url = ""
original_url = ""
page_percentage = 0
first_page_data = ""
all_pages = 0
got_product_page = False
product_page_dict = []
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


def get_proxies():  # getting proxies by scrapping the site for free
    url3 = 'https://free-proxy-list.net/'
    response = requests.get(url3)
    parser = fromstring(response.text)
    proxies = set()

    for i in parser.xpath('//tbody/tr')[:200]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            print(proxies)
    return proxies


def get_pro_proxies():  # getting proxies from the paid api
    proxies = set()
    url5 = 'http://list.didsoft.com/get?email=thomas@letspondr.com&pass=gfmubt&pid=http3000&showcountry=no'
    response = requests.get(url5)
    ip_string = response.text
    for proxy in ip_string.splitlines():
        print(proxy)
        proxies.add(proxy)
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
            # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
            # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
            print("Skipping. Connnection error")


def scrape(url2, ip_index, thread_number):
    if page_percentage >= 90:  # change for more or less page percentage
        return None
    else:
        # Create an Extractor by reading from the YAML file
        e = Extractor.from_yaml_file('selectors.yml')
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

        # Pick a random browser headers
        headers = random.choice(headers_list)
        # Create a request session
        site_response = requests.Session()
        site_response.headers = headers
        # Download the page using requests
        print("Downloading %s" % url2)
        try:
            print(working_ip[randint])  # if working ip was deleted (index out of range)
        except:
            randint = random.randint(0, len(working_ip) - 1)  # assign a new randint
            old_randints[thread_number - 1] = randint

        print('current proxy ' + working_ip[randint])
        stop_count = 0
        r = ''
        while r == '':
            try:
                r = site_response.get(url2, headers=headers, proxies={"http": working_ip[randint],
                                                                      "https": working_ip[randint]}, timeout=45)
                break
            except:
                if page_percentage >= 90:  # change for more or less page percentage
                    break
                sleep_time = 5
                print("Connection refused by the server..")
                print("Let me sleep for " + str(sleep_time) + " seconds")
                print("ZZzzzz...")
                time.sleep(sleep_time)
                print("Was a nice sleep, now let me continue...")
                stop_count = stop_count + 1
                print("stop count " + str(stop_count))
                if stop_count > 3:
                    randint = random.randint(0, len(working_ip) - 1)  # try to assign this to the global ip array
                    old_randints[thread_number - 1] = randint
                    # print('to many stops, reassigning randint')
                    stop_count = 0
                continue
        # Simple check to check if page was blocked (Usually 503)
        if page_percentage >= 90:  # change for more or less page percentage
            return None
        print(str(r.status_code))
        return e.extract(r.text)


def get_product_page(front_url):
    global product_page_dict

    product_info = {}
    product_info['name'] = 0
    PROXY = working_ip[random.randint(0, len(working_ip) - 1)]
    print("@@@@@@ getting product page @@@@@@")

    while product_info['name'] == 0:
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server=%s' % PROXY)
            driver = webdriver.Chrome(chrome_options=chrome_options,
                                      executable_path="/usr/lib/chromium-browser/chromedriver")

            print('starting download...')
            url = front_url
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//span[@id="productTitle"]')))
            try:
                name = driver.find_element_by_xpath('//span[@id="productTitle"]')
                product_info['name'] = name.text.strip()
            except:
                product_info['name'] = 0
            try:
                price = driver.find_element_by_xpath("(//span[contains(@class,'a-color-price')])[1]")
                product_info['price'] = price.text
            except:
                product_info['price'] = 0
            try:
                category = driver.find_element_by_xpath("(//span[@class='a-list-item']/a)[last()]")
                product_info['category'] = category.text.strip()
            except:
                product_info['category'] = 0
            try:
                feature_bullets = driver.find_element_by_xpath('//*[@id="feature-bullets"]')
                product_info['feature_bullets'] = feature_bullets.text
            except:
                product_info['feature_bullets'] = 0
            try:
                images = [my_elem.get_attribute("src") for my_elem in WebDriverWait(driver, 20).until(
                    EC.visibility_of_all_elements_located(
                        (By.XPATH, "//div[@id='altImages']/ul//li[@data-ux-click]//img")))]
                product_info['images'] = images
            except:
                product_info['images'] = 0
            try:
                long_description = driver.find_element_by_xpath(
                    '/html/body/div[1]/div[3]/div[9]/div[28]/div/div[2]/div/div/div/div[2]/p')
                product_info['long_description'] = long_description.text
            except:
                product_info['long_description'] = 0
        except:
            print('proxy took to long, trying new proxy')
            PROXY = working_ip[random.randint(0, len(working_ip) - 1)]

    product_page_dict.append(product_info)  # Append scrape to dictionary
    print(str(len(product_page_dict)) + ' . ', end='')  # print the current length of the scrapes

    print(product_page_dict)


def get_page_num(url2):
    # Create an Extractor by reading from the YAML file
    e = Extractor.from_yaml_file('selectors.yml')
    global headers
    # Create ordered dict from Headers above
    ordered_headers_list = []

    for headers in headers_list:
        h = OrderedDict()
        for header, value in headers.items():
            h[header] = value
        ordered_headers_list.append(h)
    # Pick a random browser headers
    headers = random.choice(headers_list)
    # Create a request session
    site_response = requests.Session()
    site_response.headers = headers
    # Download the page using requests
    print("Downloading %s" % url2)
    current_ip = random.randint(0, len(working_ip) - 1)
    print('current proxy ' + working_ip[current_ip])
    stop_count = 0
    r = ''
    while r == '':
        try:
            r = site_response.get(url2, headers=headers, proxies={"http": working_ip[current_ip],
                                                                  "https": working_ip[current_ip]}, timeout=45)
            if e.extract(r.text)['reviews'] is None:
                print('Amazon blocked so new ip')
                current_ip = random.randint(0, len(working_ip) - 1)
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

    data = e.extract(r.text)
    for r in data['reviews']:
        r["product"] = data["product_title"]
        r['url'] = scrape_url + '1'
        if 'verified' in r:
            if r['verified'] is None:
                r['verified'] = 'No'
            elif 'Verified Purchase' in r['verified']:  # not sure if nessesary
                r['verified'] = 'Yes'
            else:
                r['verified'] = 'Yes'
            if r['rating'] is None: r['rating'] = '3'  # change this @@@@@@@@@@@
        r['rating'] = r['rating'].split(' out of')[0]
        date_posted = r['date'].split('on ')[-1]
        if r['images']:
            r['images'] = "\n".join(r['images'])
        r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
        r['content'] = r['content'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
        if 'Your browser does not support HTML5 video.' in r['content']:
            r['content'] = r['content'].replace('your browser does not support html5 video', '')
        if r['title'] is None:
            r['title'] = ''
        else:
            r['title'] = r['title'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
        r['author'] = r['author'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
        csv_outfile.append(r)
        txt_outfile.append(r['content'] + "\n")
    global total_pages_scrapped
    total_pages_scrapped = total_pages_scrapped + 1

    return_string = data['review_number']
    search_string = re.search('ratings (.+?)global reviews', return_string)
    search_string = search_string.group(1)
    search_string = search_string.replace('|', '')
    search_string = search_string.replace(',', '')
    page_int = int(float(search_string))
    page_int = int(page_int / 10) + 1
    global all_pages
    all_pages = page_int


def run_scrapping(url_to_scrape):
    global scrape_url
    global thread  # this is global for joining later
    global old_randints  # including old_randints as global
    global proxy_pool
    global all_pages
    scrape_url = url_to_scrape
    scrape_url = scrape_url.rstrip()
    print(scrape_url)

    if '/dp/' in scrape_url:
        end_of_link = scrape_url.split('/dp/')[1]
        productId = end_of_link[0:10]
    elif 'product/' in scrape_url:
        end_of_link = scrape_url.split('product/')[1]
        productId = end_of_link[0:10]

    scrape_url = 'https://www.amazon.com/product-reviews/' + productId + '/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber='

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

    # productThreads = []
    # product_index = 0
    # while product_index < 11:
    #    product_page_thread = Thread(target=get_product_page, args=(url_to_scrape,))
    #    productThreads.append(product_page_thread)
    #    product_page_thread.start()
    #    product_index = product_index + 1
    # product_page_thread = Thread(target=get_product_page, args=(url_to_scrape,))
    # product_page_thread.start()
    get_product_page(url_to_scrape)
    time.sleep(1)
    get_page_num(scrape_url + '1')

    if all_pages > 100:
        all_pages = 100
    print(all_pages)

    pages_per_thread = 1
    num_of_loops = int(all_pages / pages_per_thread)  # how many loops/ threads are needed
    tens = 2  # the lower bound of the scrape() method
    old_randints = old_randints * num_of_loops  # making a list of size num_of_loops for proxy_index storage

    scrape_threads = []

    print('@@@@ starting @@@@')
    i = 2
    while i <= num_of_loops:
        time.sleep(1)
        old_randints[i - 1] = random.randint(0, len(working_ip) - 1)
        print("current loop " + str(i))
        thread = Thread(target=collect_data, args=(tens, (i * pages_per_thread) + 1, all_pages, i))
        tens = tens + pages_per_thread
        i = i + 1
        scrape_threads.append(thread)
        thread.start()
        # fix not 10s bug here!!

    for t in scrape_threads:
        t.join()

    # for t in productThreads:
    #    t.join()

    return csv_outfile, txt_outfile, product_page_dict[0]['price'], product_page_dict[0]['images'], \
           product_page_dict[0]['feature_bullets'], product_page_dict[0]['long_description']


def collect_data(lower_page, higher_page, all_pages, thread_number):
    global total_pages_scrapped
    global page_percentage
    for i in range(lower_page, higher_page):

        data = scrape(scrape_url + str(i), old_randints[thread_number - 1], thread_number)
        # appends the page number to the end of the url
        if data is None:
            print('exiting!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            sys.exit()  # exiting if the percentage is 90 or more
        else:
            while data['reviews'] is None:
                try:
                    print('Amazon blocked so scrapping again')
                    print(old_randints[thread_number - 1])
                    print('ip deleting ' + working_ip[old_randints[thread_number - 1]])
                    del working_ip[old_randints[thread_number - 1]]
                    if len(working_ip) < 5:
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

                    old_randints[thread_number - 1] = random.randint(0, len(working_ip) - 1)
                except:
                    print('ip already deleted, assigning new randint')
                    old_randints[thread_number - 1] = random.randint(0, len(working_ip) - 1)

                data = scrape(scrape_url + str(i), old_randints[thread_number - 1], thread_number)
                if data is None:
                    print('exiting!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    sys.exit()  # exiting if the percentage is 90 or more

            if data:
                for r in data['reviews']:
                    r["product"] = data["product_title"]
                    r['url'] = scrape_url + str(i)
                    if 'verified' in r:
                        if r['verified'] is None:
                            r['verified'] = 'No'
                        elif 'Verified Purchase' in r['verified']:  # not sure if nessesary
                            r['verified'] = 'Yes'
                        else:
                            r['verified'] = 'Yes'
                        if r['rating'] is None: r['rating'] = '3'  # change this @@@@@@@@@@@
                    r['rating'] = r['rating'].split(' out of')[0]
                    date_posted = r['date'].split('on ')[-1]
                    if r['images']:
                        r['images'] = "\n".join(r['images'])
                    r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
                    r['content'] = r['content'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
                    if 'Your browser does not support HTML5 video.' in r['content']:
                        r['content'] = r['content'].replace('your browser does not support html5 video', '')
                    if r['title'] is None:
                        r['title'] = ''
                    else:
                        r['title'] = r['title'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
                    r['author'] = r['author'].encode('ascii', 'ignore').decode('ascii')  # gets rid of emojis!
                    # writer.writerow(r)
                    csv_outfile.append(r)
                    # gptoutfile.write(r['content'] + "\n")
                    txt_outfile.append(r['content'] + "\n")
                    print(str(r))
                total_pages_scrapped = total_pages_scrapped + 1
                page_percentage = round((total_pages_scrapped / all_pages) * 100, 2)
                print(str(page_percentage) + "%")
                # sleep(random.randint(1, 2))


# lower page has to start at 1

if __name__ == '__main__':
    run_scrapping(scrape_url)
