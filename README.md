# Pondr Groundhog Engine
Authors: Abhi Balijepalli, Thomas Stahura

This is Pondr's brain, it runs all the AI analysis using OpenAI GPT-3 and web scrapping of amazon's product page. After it does series of tasks in parallel, it uploads all the graphs and metrics to firestore. The groundhog-engine either runs on `Apache Airflow` or a `cron server` with high GPU capabilities. 

### To get setup:
1. `pip3 install -r requirements.txt` #if you are having dependency errors launch python3.7 or higher in a virtual env.
2. `python3 main.py` #follow the instructions below before you run `main.py`

### Instructions:
1. Copy paste desired url into url.txt, specify pages scrapped and run main(). 
   - example url = `https://www.amazon.com/Marcato-8320-Machine-Cutter-Instructions/dp/B0009U5OSO/?_encoding=UTF8&pd_rd_w=ExlFg&pf_rd_p=1e39a1ef-b4a3-4740-8b17-1bf4a436b01b&pf_rd_r=4F7G8ND3W3ZQG68MQXJH&pd_rd_r=af07ae27-a06e-47b1-b342-8f8fe722524f&pd_rd_wg=sxuAL&ref_=pd_gw_unk`
2. Disable the POST and GET function that check our waitlist for a queue of products to be scanned. 
3. Spend time understanding the flow of all the files

### What each script does:
- `reviews.py`: takes in urls and scrapes amazon product data
- `models.py`: anlysis the data and outputs package.json which can be sent to Pondr Admin API
- `GPT-3.py`: answers questions using reviews as examples, need Open AI GPT-3 API key
- `api.py`: communicates with the Pondr Admin API, make sure to download API and run locally
