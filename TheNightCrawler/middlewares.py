# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


from scrapy import signals
from scrapy.http import HtmlResponse
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from random import choice
import requests
import logging
import undetected_chromedriver as uc

logging.getLogger('seleniumwire').setLevel(logging.WARNING)


class SeleniumWithUndetectedBrowser:
    """
    Using selenium undetected browser
    """

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        middleware.crawler = crawler
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def __init__(self, settings):
        self.crawler = None
        self.browser = None

    def spider_opened(self, spider):
        spider.logger.info(f"Selenium With Undetected Browser Middleware Initiated")

    def _createBrowser(self, headless=True):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Launching a Selenium Undetected Webdriver/Browser Session
        """
        spider.logger.info(f"Creating new browser session")
        chrome_options = uc.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")  # Running Selenium Session with no UI.

        browser = uc.Chrome(version_main=146, options=chrome_options)

        spider.logger.info(f"\n{'=' * 80}")
        spider.logger.info(f"Undetected Browser Active Capabilities")
        print(browser.capabilities)
        spider.logger.info(f"{'=' * 80}\n")

        return browser

    def _makeSeleniumRequest(self, url, browser, waitSelector=None, waitTime=10, actions=None):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Make selenium request
        :param url: URL to make request
        :param browser: Selenium webdriver
        :param waitSelector: Specified a wait until a specific CSS selector is loaded
        :param waitTime: Wait time for response to be fully loaded before analyzing the HTML content
        :param actions: Execute custom actions
        """
        spider.logger.info(f"Making Selenium request to: {url}")
        try:
            browser.set_page_load_timeout(waitTime)
            try:
                browser.get(url)
            except TimeoutException:
                spider.logger.info(f"Page load timed out at {waitTime}s for {url}, attempting to proceed...")

            if waitSelector:
                try:
                    spider.logger.info(f"Waiting for selector: {waitSelector}")
                    WebDriverWait(browser, waitTime).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, waitSelector)))
                    spider.logger.info(f"Selector found: {waitSelector}")
                except Exception as e:
                    spider.logger.warning(f"Wait timeout for selector '{waitSelector}': {e}")

            if actions and callable(actions):
                spider.logger.info("Executing custom actions")
                actions(browser)

            EncodedResponseBody = browser.page_source.encode('utf-8')
            currentUrl = browser.current_url
            statusCode = 200 # NOTE: UC does not have status code features, so we have to blindly assume the status code as 200
            return statusCode, EncodedResponseBody, currentUrl
        except Exception as e:
            spider.logger.error(f"Selenium request error: {e}")
            return 500, None, url

    def process_request(self, request):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        spider.logger.info(f"\n{'=' * 80}")
        spider.logger.info(f"SELENIUM REQUEST PROCESSING")
        spider.logger.info(f"URL: {request.url}")
        spider.logger.info(f"{'=' * 80}\n")

        spider.logger.info("Opening new browser")
        self.browser = self._createBrowser(request.meta.get('headless', False))

        waitSelector = request.meta.get('selenium_wait_selector')
        timeOut = request.meta.get('selenium_wait_time', 10)
        actions = request.meta.get('selenium_actions')
        statusCode, EncodedResponseBody, currentUrl = self._makeSeleniumRequest(request.url, self.browser, waitSelector, timeOut, actions)

        if EncodedResponseBody:
            request.meta['selenium_browser'] = self.browser
            response = HtmlResponse(url=currentUrl, body=EncodedResponseBody, encoding='utf-8', request=request, status=statusCode)
            return response

        return None

    def process_exception(self, request, exception):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        spider.logger.error(f"\n{'=' * 80}")
        spider.logger.error(f"EXCEPTION IN SELENIUM REQUEST")
        spider.logger.error(f"Exception Type: {type(exception).__name__}")
        spider.logger.error(f"Exception Message: {str(exception)}")
        spider.logger.error(f"URL: {request.url}")

        """Create a new retry request with ScapeOPS proxy"""
        spider.logger.warning(f"Exception: {exception.__class__.__name__} - Retrying")
        if self.browser:
            spider.logger.info("Closing browser due to exception")
            self.browser.quit()
        return None


class SeleniumWithScrapeOpsProxy:
    """
    Using selenium driver for headless dynamic scrape with ScrapeOps Browser Header and Proxy
    """

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        middleware.crawler = crawler
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def __init__(self, settings):
        self.crawler = None
        self.scrapeOpsAPI = settings.get('SCRAPEOPSAPI')

        """ScrapeOPS Proxy"""
        self.scrapeOpsProxyEnabled = settings.get('SCRAPEOPSPROXYENABLED', False)

        "ScrapeOPS Fake Browser Headers"
        self.scrapeOpsHeadersEndpoint = "https://headers.scrapeops.io/v1/browser-headers"
        self.scrapeOpsBrowserHeaderActive = settings.get('SCRAPEOPSBROWSERHEADERSACTIVE', False)
        self.scrapeOpsNumResults = settings.get('SCRAPEOPSBROWSERHEADERSNUMRESULTS', 50)
        self.browserHeaders = []
        self.browser = None

    def spider_opened(self, spider):
        spider.logger.info(f"Selenium With ScrapeOPS Proxy Middleware Initiated")

    def _getBrowserHeaders(self, mobileHeaders):
        spider = self.crawler.spider if self.crawler else None
        if self.scrapeOpsBrowserHeaderActive:
            if self.scrapeOpsAPI:
                try:
                    if mobileHeaders:
                        spider.logger.info(f"Fetching mobile headers from ScrapeOps")
                        payload = {'api_key': self.scrapeOpsAPI, 'num_results': self.scrapeOpsNumResults, 'mobile': 'true'}
                    else:
                        spider.logger.info(f"Fetching non-mobile device headers from ScrapeOps")
                        payload = {'api_key': self.scrapeOpsAPI, 'num_results': self.scrapeOpsNumResults, 'mobile': 'false'}
                    response = requests.get(self.scrapeOpsHeadersEndpoint, params=payload)
                    self.browserHeaders = response.json().get('result', [])
                    spider.logger.info(f"Fetched {len(self.browserHeaders)} browser headers from ScrapeOps")
                except Exception as e:
                    spider.logger.error(f"Error fetching browser headers: {e}")
                    self.browserHeaders = []
            else:
                spider.logger.warning(f"ScrapeOps API key missing")
        else:
            spider.logger.warning(f"ScrapeOps Fake Browser Header is disabled")

    def _getRandomBrowserHeader(self):
        return choice(self.browserHeaders) if self.browserHeaders else {}

    def _createBrowser(self,  browserHeader=None, headless=True):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Launching a Selenium Webdriver/Browser Session
        :param browserHeader: ScrapeOps Fake Browser Header to configure Selenium to use
        :param headless: Determine whether to run headless or not
        """

        spider.logger.info(f"Creating new browser session with ScrapeOPS Proxy")

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  # Running Selenium Session with no UI.
        chrome_options.add_argument('--no-sandbox')  # Enable the spider to run web scrape in real life browser.
        chrome_options.add_argument('--disable-dev-shm-usage')  # Disable shared memory feature that could cause the Selenium Chromium session to crash.
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # IMPORTANT: Remove the navigator.webdriver flag that websites use to detect Selenium. Selenium default set this to true.
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])  # IMPORTANT: Removes the "Chrome is being controlled by automated test software" banner and prevent Chrome form adding automation-related command -line switches.
        chrome_options.add_experimental_option('useAutomationExtension',False)  # IMPORTANT: Disables Chrome's automation extension that Selenium normally loads. This limit the bot detection surface.

        """Configuring Selenium To Use Fake ScrapeOps User Agent"""
        if browserHeader:
            userAgent = browserHeader.get('user-agent')
            if userAgent:
                chrome_options.add_argument(f'user-agent={userAgent}')
                spider.logger.info(f"Using ScrapeOps fake user agent: {userAgent}")

        if self.scrapeOpsProxyEnabled:
            if self.scrapeOpsAPI:
                proxyOptions = {
                    'proxy': {
                        'http': f'http://scrapeops.headless_browser_mode=true:{self.scrapeOpsAPI}@proxy.scrapeops.io:5353',
                        'https': f'http://scrapeops.headless_browser_mode=true:{self.scrapeOpsAPI}@proxy.scrapeops.io:5353',
                        'no_proxy': 'localhost:127.0.0.1'
                    }
                }
                browser = webdriver.Chrome(options=chrome_options, seleniumwire_options=proxyOptions)

                def interceptor(request):
                    # stopping images from being requested
                    # in case any are not blocked by imagesEnabled=false in the webdriver options above
                    if request.path.endswith(('.png', '.jpg', '.gif')):
                        request.abort()

                    # stopping fonts from being requested
                    if 'fonts.' in request.path:  # eg fonts.googleapis.com or fonts.gstatic.com
                        request.abort()

                    pass

                browser.request_interceptor = interceptor

            else:
                spider.logger.warning(f"ScrapeOps API key missing")
                browser = webdriver.Chrome(options=chrome_options)
        else:
            spider.logger.warning(f"ScrapeOps Proxy is disabled")
            browser = webdriver.Chrome(options=chrome_options)

        """Configuring Selenium To Use Fake ScrapeOps Browser Headers"""
        if browserHeader and hasattr(browser, 'execute_cdp_cmd'):
            headers_to_set = {}
            for key, value in browserHeader.items():
                if key not in ['user-agent']:
                    headers_to_set[key] = value

            if headers_to_set:
                browser.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': headers_to_set})
                spider.logger.info(f"Set {len(headers_to_set)} additional headers via CDP")
                spider.logger.info(f"Using ScrapeOps browser header: {browserHeader}")

        return browser

    def _makeSeleniumRequest(self, url, browser, waitSelector=None, waitTime=10, actions=None):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Make selenium request
        :param url: URL to make request
        :param browser: Selenium webdriver
        :param waitSelector: Specified a wait until a specific CSS selector is loaded
        :param waitTime: Wait time for response content to fully loaded before processing the HTML content
        :param actions: Execute custom actions
        """
        spider.logger.info(f"Making Selenium request to: {url}")

        try:
            browser.set_page_load_timeout(waitTime)
            try:
                browser.get(url)
            except TimeoutException:
                spider.logger.info(f"Page load timed out at {waitTime}s for {url}, attempting to proceed...")

            if waitSelector:
                try:
                    spider.logger.info(f"Waiting for selector: {waitSelector}")
                    WebDriverWait(browser, waitTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, waitSelector)))
                    spider.logger.info(f"Selector found: {waitSelector}")
                except Exception as e:
                    spider.logger.warning(f"Wait timeout for selector '{waitSelector}': {e}")
            if actions and callable(actions):
                spider.logger.info("Executing custom actions")
                actions(browser)

            EncodedResponseBody = browser.page_source.encode('utf-8')
            currentUrl = browser.current_url
            statusCode = 200
            for request in reversed(browser.requests):
                if request.response:
                    if request.url == currentUrl or (request.url.rstrip('/') == currentUrl.rstrip('/')):
                        statusCode = request.response.status_code
                        spider.logger.info(f"Final page status for {currentUrl}: {statusCode}")
                        break
            return statusCode, EncodedResponseBody, currentUrl
        except Exception as e:
            spider.logger.error(f"Selenium request error: {e}")
            return 500, None, url

    def process_request(self, request):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        mobileHeader = request.meta.get('use_mobile_headers', False)

        self._getBrowserHeaders(mobileHeader)

        spider.logger.info(f"\n{'=' * 80}")
        spider.logger.info(f"SELENIUM REQUEST PROCESSING")
        spider.logger.info(f"URL: {request.url}")
        spider.logger.info(f"{'=' * 80}\n")

        """Using Fake Browser Header"""
        browserHeader = self._getRandomBrowserHeader()
        spider.logger.info(f"Using fake browser headers:\n{browserHeader}")


        self.browser = self._createBrowser(browserHeader, request.meta.get('headless', False))

        waitSelector = request.meta.get('selenium_wait_selector')
        timeOut = request.meta.get('selenium_wait_time', 10)
        actions = request.meta.get('selenium_actions')

        statusCode, EncodedResponseBody, currentUrl = self._makeSeleniumRequest(request.url, self.browser, waitSelector, timeOut, actions)

        if EncodedResponseBody:
            request.meta['selenium_browser'] = self.browser
            response = HtmlResponse(url=currentUrl, body=EncodedResponseBody, encoding='utf-8', request=request, status=statusCode)
            return response

        return None

    def process_exception(self, request, exception):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        spider.logger.error(f"\n{'=' * 80}")
        spider.logger.error(f"EXCEPTION IN SELENIUM REQUEST")
        spider.logger.error(f"Exception Type: {type(exception).__name__}")
        spider.logger.error(f"Exception Message: {str(exception)}")
        spider.logger.error(f"URL: {request.url}")
        if self.browser:
            spider.logger.error("Closing browser due to exception")
            self.browser.quit()
        return None


class SeleniumWithScrapeOpsBrowserHeader:
    """
    Using selenium driver for headless dynamic scrape with ScrapeOps Customized Browser Headers integration
    """

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        middleware.crawler = crawler
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def __init__(self, settings):
        self.crawler = None
        self.scrapeOpsAPI = settings.get('SCRAPEOPSAPI')

        "ScrapeOPS Fake Browser Headers"
        self.scrapeOpsHeadersEndpoint = "https://headers.scrapeops.io/v1/browser-headers"
        self.scrapeOpsBrowserHeaderActive = settings.get('SCRAPEOPSBROWSERHEADERSACTIVE', False)
        self.scrapeOpsNumResults = settings.get('SCRAPEOPSBROWSERHEADERSNUMRESULTS', 50)
        self.browserHeaders = []
        self.browser = None

    def spider_opened(self, spider):
        spider.logger.info(f"Selenium With ScrapeOPS Browser Header Middleware Initiated")

    def _getBrowserHeaders(self, mobileHeaders):
        spider = self.crawler.spider if self.crawler else None
        if self.scrapeOpsBrowserHeaderActive:
            if self.scrapeOpsAPI:
                try:
                    if mobileHeaders:
                        spider.logger.info(f"Fetching mobile headers from ScrapeOps")
                        payload = {'api_key': self.scrapeOpsAPI, 'num_results': self.scrapeOpsNumResults, 'mobile': 'true'}
                    else:
                        spider.logger.info(f"Fetching non-mobile device headers from ScrapeOps")
                        payload = {'api_key': self.scrapeOpsAPI, 'num_results': self.scrapeOpsNumResults, 'mobile': 'false'}
                    response = requests.get(self.scrapeOpsHeadersEndpoint, params=payload)
                    self.browserHeaders = response.json().get('result', [])
                    spider.logger.info(f"Fetched {len(self.browserHeaders)} browser headers from ScrapeOps")
                except Exception as e:
                    spider.logger.error(f"Error fetching browser headers: {e}")
                    self.browserHeaders = []
            else:
                spider.logger.warning(f"ScrapeOps API key is missing")
        else:
            spider.logger.warning(f"ScrapeOps Fake Browser Header is disabled")

    def _getRandomBrowserHeader(self):
        return choice(self.browserHeaders) if self.browserHeaders else {}

    def _createBrowser(self, browserHeader=None, headless=True):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Launching a Selenium Webdriver/Browser Session
        :param browserHeader: ScrapeOps Fake Browser Header to configure Selenium to use
        :param headless: Use headless mode or not
        """

        spider.logger.info(f"Creating new browser session")

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless") # Running Selenium Session with no UI.
        chrome_options.add_argument('--no-sandbox') # Enable the spider to run web scrape in real life browser.
        chrome_options.add_argument('--disable-dev-shm-usage') # Disable shared memory feature that could cause the Selenium Chromium session to crash.
        chrome_options.add_argument('--disable-blink-features=AutomationControlled') # IMPORTANT: Remove the navigator.webdriver flag that websites use to detect Selenium. Selenium default set this to true.
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) # IMPORTANT: Removes the "Chrome is being controlled by automated test software" banner and prevent Chrome form adding automation-related command -line switches.
        chrome_options.add_experimental_option('useAutomationExtension', False) # IMPORTANT: Disables Chrome's automation extension that Selenium normally loads. This limit the bot detection surface.

        """Configuring Selenium To Use Fake ScrapeOps User Agent"""
        if browserHeader:
            userAgent = browserHeader.get('user-agent')
            if userAgent:
                chrome_options.add_argument(f'user-agent={userAgent}')
                spider.logger.info(f"Using ScrapeOps fake user agent: {userAgent}")


        browser = webdriver.Chrome(options=chrome_options)

        """Configuring Selenium To Use Fake ScrapeOps Browser Headers"""
        if browserHeader and hasattr(browser, 'execute_cdp_cmd'):
            headers_to_set = {}
            for key, value in browserHeader.items():
                if key not in ['user-agent']:
                    headers_to_set[key] = value

            if headers_to_set:
                browser.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': headers_to_set})
                spider.logger.info(f"Set {len(headers_to_set)} additional headers via CDP")
                spider.logger.info(f"Using ScrapeOps browser header: {browserHeader}")

        return browser

    def _makeSeleniumRequest(self, url, browser, waitSelector=None, waitTime=10, actions=None):
        spider = self.crawler.spider if self.crawler else None

        """
        Description: Make selenium request
        :param url: URL to make request
        :param browser: Selenium webdriver
        :param waitSelector: Specified a wait until a specific CSS selector is loaded
        :param waitTime: Wait time for response to fully loaded before analyzing the HTML content
        :param actions: Execute custom actions
        """

        spider.logger.info(f"Making Selenium request to: {url}")

        try:
            browser.set_page_load_timeout(waitTime)
            try:
                browser.get(url)
            except TimeoutException:
                spider.logger.info(f"Page load timed out at {waitTime}s for {url}, attempting to proceed...")

            if waitSelector:
                try:
                    spider.logger.info(f"Waiting for selector: {waitSelector}")
                    WebDriverWait(browser, waitTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, waitSelector)))
                    spider.logger.info(f"Selector found: {waitSelector}")
                except Exception as e:
                    spider.logger.warning(f"Wait timeout for selector '{waitSelector}': {e}")

            if actions and callable(actions):
                spider.logger.info("Executing custom actions")
                actions(browser)

            EncodedResponseBody = browser.page_source.encode('utf-8')
            currentUrl = browser.current_url
            statusCode = 200
            for request in reversed(browser.requests):
                if request.response:
                    if request.url == currentUrl or (request.url.rstrip('/') == currentUrl.rstrip('/')):
                        statusCode = request.response.status_code
                        spider.logger.info(f"Final page status for {currentUrl}: {statusCode}")
                        break
            return statusCode, EncodedResponseBody, currentUrl
        except Exception as e:
            spider.logger.error(f"Selenium request error: {e}")
            return 500, None, url

    def process_request(self, request):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        mobileHeader = request.meta.get('use_mobile_headers', False)

        self._getBrowserHeaders(mobileHeader)

        spider.logger.info(f"\n{'=' * 80}")
        spider.logger.info(f"SELENIUM REQUEST PROCESSING")
        spider.logger.info(f"URL: {request.url}")
        spider.logger.info(f"{'=' * 80}\n")

        """Using Fake Browser Header"""
        browserHeader = self._getRandomBrowserHeader()
        spider.logger.info(f"Using fake browser headers:\n{browserHeader}")

        spider.logger.info("Opening new browser")
        self.browser = self._createBrowser(browserHeader, request.meta.get('headless', False))

        waitSelector = request.meta.get('selenium_wait_selector')
        timeOut = request.meta.get('selenium_wait_time', 10)
        actions = request.meta.get('selenium_actions')
        statusCode, EncodedResponseBody, currentUrl = self._makeSeleniumRequest(request.url, self.browser, waitSelector, timeOut, actions)
        if EncodedResponseBody:
            request.meta['selenium_browser'] = self.browser
            response = HtmlResponse(url=currentUrl, body=EncodedResponseBody, encoding='utf-8', request=request, status=statusCode)
            return response

        return None

    def process_exception(self, request, exception):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        spider.logger.error(f"\n{'=' * 80}")
        spider.logger.error(f"EXCEPTION IN SELENIUM REQUEST")
        spider.logger.error(f"Exception Type: {type(exception).__name__}")
        spider.logger.error(f"Exception Message: {str(exception)}")
        spider.logger.error(f"URL: {request.url}")

        """Create a new retry request with ScapeOPS proxy"""
        spider.logger.warning(f"Exception: {exception.__class__.__name__} - Retrying")
        if self.browser:
            spider.logger.info("Closing browser due to exception")
            self.browser.quit()
        return None


class SeleniumWithNothingMiddleware:
    """
    Using selenium driver for headless dynamic scrape with nothing
    """

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        middleware.crawler = crawler
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def __init__(self, settings):
        self.crawler = None
        self.browser = None

    def spider_opened(self, spider):
        spider.logger.info(f"Pure Selenium Middleware Initiated")

    def _createBrowser(self, headless=True):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Launching a Selenium Webdriver/Browser Session
        """
        spider.logger.info(f"Creating new browser session")
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless") # Running Selenium Session with no UI.
        chrome_options.add_argument('--no-sandbox') # Enable the spider to run web scrape in real life browser.
        chrome_options.add_argument('--disable-dev-shm-usage') # Disable shared memory feature that could cause the Selenium Chromium session to crash.
        chrome_options.add_argument('--disable-blink-features=AutomationControlled') # IMPORTANT: Remove the navigator.webdriver flag that websites use to detect Selenium. Selenium default set this to true.
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) # IMPORTANT: Removes the "Chrome is being controlled by automated test software" banner and prevent Chrome form adding automation-related command -line switches.
        chrome_options.add_experimental_option('useAutomationExtension', False) # IMPORTANT: Disables Chrome's automation extension that Selenium normally loads. This limit the bot detection surface.

        browser = webdriver.Chrome(options=chrome_options)
        return browser

    def _makeSeleniumRequest(self, url, browser, waitSelector=None, waitTime=10, actions=None):
        spider = self.crawler.spider if self.crawler else None
        """
        Description: Make selenium request
        :param url: URL to make request
        :param browser: Selenium webdriver
        :param waitSelector: Specified a wait until a specific CSS selector is loaded
        :param waitTime: Wait time for response to be fully loaded before analyzing the HTML content
        :param actions: Execute custom actions
        """
        spider.logger.info(f"Making Selenium request to: {url}")
        try:
            browser.set_page_load_timeout(waitTime)
            try:
                browser.get(url)
            except TimeoutException:
                spider.logger.info(f"Page load timed out at {waitTime}s for {url}, attempting to proceed...")

            if waitSelector:
                try:
                    spider.logger.info(f"Waiting for selector: {waitSelector}")
                    WebDriverWait(browser, waitTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, waitSelector)))
                    spider.logger.info(f"Selector found: {waitSelector}")
                except Exception as e:
                    spider.logger.warning(f"Wait timeout for selector '{waitSelector}': {e}")

            if actions and callable(actions):
                spider.logger.info("Executing custom actions")
                actions(browser)


            EncodedResponseBody = browser.page_source.encode('utf-8')
            currentUrl = browser.current_url
            statusCode = 200
            for request in reversed(browser.requests):
                if request.response:
                    if request.url == currentUrl or (request.url.rstrip('/') == currentUrl.rstrip('/')):
                        statusCode = request.response.status_code
                        spider.logger.info(f"Final page status for {currentUrl}: {statusCode}")
                        break
            return statusCode, EncodedResponseBody, currentUrl
        except Exception as e:
            spider.logger.error(f"Selenium request error: {e}")
            return 500, None, url

    def process_request(self, request):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        spider.logger.info(f"\n{'=' * 80}")
        spider.logger.info(f"SELENIUM REQUEST PROCESSING")
        spider.logger.info(f"URL: {request.url}")
        spider.logger.info(f"{'=' * 80}\n")

        spider.logger.info("Opening new browser")
        self.browser = self._createBrowser(request.meta.get('headless', False))

        waitSelector = request.meta.get('selenium_wait_selector')
        timeOut = request.meta.get('selenium_wait_time', 10)
        actions = request.meta.get('selenium_actions')
        statusCode, EncodedResponseBody, currentUrl = self._makeSeleniumRequest(request.url, self.browser, waitSelector, timeOut, actions)


        if EncodedResponseBody:
            request.meta['selenium_browser'] = self.browser
            response = HtmlResponse(url=currentUrl, body=EncodedResponseBody, encoding='utf-8', request=request, status=statusCode)
            return response

        return None

    def process_exception(self, request, exception):
        spider = self.crawler.spider if self.crawler else None
        if not request.meta.get('use_selenium'):
            return None

        spider.logger.error(f"\n{'=' * 80}")
        spider.logger.error(f"EXCEPTION IN SELENIUM REQUEST")
        spider.logger.error(f"Exception Type: {type(exception).__name__}")
        spider.logger.error(f"Exception Message: {str(exception)}")
        spider.logger.error(f"URL: {request.url}")

        """Create a new retry request with ScapeOPS proxy"""
        spider.logger.warning(f"Exception: {exception.__class__.__name__} - Retrying")
        if self.browser:
            spider.logger.info("Closing browser due to exception")
            self.browser.quit()
        return None
