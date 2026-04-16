# The Night Crawler

   A web crawler integrated with Python Scrapy using five different methods: Pure Selenium Browser, Selenium Browser with customized non-mobile browser request headers, Selenium Browser with customized mobile browser request headers, Selenium Browser with ScrapeOPS Proxy, and undetected chrome driver to bypass website invisible CAPTCHA.

## Repo Structure:

```
├── TheNightCrawler          
│   ├── Data                                               # Crawling Results
│   │   ├── BLUE-TEAM-WEBSITE                              # Resulting webpage screenshots and HTML from a self made website with self made CAPTCHA algorithm by the Blue Team
│   │   │   ├── Mobile-GUI                                 # Crawling Result using Mobile Header Method with Selenium browser GUI enabled
│   │   │   ├── Mobile-Headless                            # Crawling Result using Mobile Header Method with Selenium browser GUI disabled
│   │   │   ├── Non-Mobile-GUI                             # Crawling Result using Non Mobile Header Method with Selenium browser GUI enabled
│   │   │   ├── Non-Mobile-Headless                        # Crawling Result using Non Mobile Header Method with Selenium browser GUI disabled
│   │   │   ├── Pure-Selenium-GUI                          # Crawling Result using pure Selenium browser GUI enabled
│   │   │   ├── Pure-Selenium-Headless                     # Crawling Result using pure Selenium browser GUI disabled
│   │   │   ├── ScrapeOPS-GUI                              # Crawling Result using ScrapeOps Proxy with Selenium browser GUI enabled
│   │   │   ├── ScrapeOPS-Headless                         # Crawling Result using ScrapeOps Proxy with Selenium browser GUI disabled
│   │   │   ├── UD-GUI                                     # Crawling Result using Undetected Chrome browser with GUI enabled
│   │   │   └── UD-Headless                                # Crawling Result using Undetected Chrome browser with GUI disabled
│   │   ├── LIVE-WEBSITES                                  # Resulting webpage screenshots and HTML from different live website with different CAPTCHA vendors
│   │   │   ├── Mobile-GUI                                 
│   │   │   ├── Mobile-Headless                            
│   │   │   ├── Non-Mobile-GUI                             
│   │   │   ├── Non-Mobile-Headless                        
│   │   │   ├── Pure-Selenium-GUI                          
│   │   │   ├── Pure-Selenium-Headless                     
│   │   │   ├── ScrapeOPSProxy-GUI                         
│   │   │   ├── ScrapeOPSProxy-Headless                    
│   │   │   ├── UD-GUI                                     
│   │   │   ├── UD-Headless                                
│   │   │   └── CrawlingResults.ipynb                      # This Jupyter Notebook will generate a bar graph showing the crawling results on the live websites with all five methods 
│   ├── spiders                                            # The directory that contains main scripts that define the crawler logic
│   │   ├── NOTES.txt                                      # Note taken on methods for the crawler to determine what CAPTCHA the current visited website is being implemented
│   │   ├── NightCrawler.py                                # The main logic of the crawler
│   │   ├── __init__.py
│   ├── items.py                                           # This script specified the crawling data fields to be saved as a csv file
│   ├── middlewares.py                                     # This script contains all the 5 crawling methods
│   ├── pipelines.py                                       # This script is a data pipeline to gather the crawling data to output to items.py and saved as csv file
│   └── settings.py                                        # This is the essential settings for the NightCrawler
├── README.md                                              # This file
└── scrapy.cfg                                             # Important Scrapy config for the whole crawler system 
```

## Instructions:

**Pure Selenium Method**

In settings.py, enable only "TheNightCrawler.middlewares.SeleniumWithNothingMiddleware": 400

```
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "TheNightCrawler.middlewares.SeleniumWithNothingMiddleware": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsBrowserHeader": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsProxy": 420,
    # "TheNightCrawler.middlewares.SeleniumWithUndetectedBrowser": 420,
    "TheNightCrawler.downloadermiddlewares.retry.RetryMiddleware": None
}
```

In the spider main script, "NightCrawler.py" at line 

## Contributors:
   1. David Nguyen - DavidNguyen1812
   2. Anirudh Maramraj - Catty-Wampus
   3. Bishesh Joshi - Wartham
   4. Diemni Dao - DiemmiDao
   5. Hiten Chintapalli - Hiten1810
   6. Joseph Nguyen - jo-ngu




 
 
