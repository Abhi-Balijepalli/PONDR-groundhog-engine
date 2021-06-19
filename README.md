# Pondr Review Scapper and Analysis

copy paste desired url into url.txt, specify pages scrapped and run main

urls must be in the form https://www.amazon.com/Wyze-Indoor-Wireless-Camera-Vision/product-reviews/B07G2YR23M/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=

What each script does:

reviews.py: takes in urls and srapes data

models.py: anlysis the data and outputs package.json which can be sent to Pondr Admin API

GPT-3.py: answers questions using reviews as examples, need Open AI GPT-3 API key

api.py: communicates with the Pondr Admin API, make sure to download API and run locally


-T.S
