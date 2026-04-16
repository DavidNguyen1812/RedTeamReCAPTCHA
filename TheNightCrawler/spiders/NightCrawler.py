import scrapy
from TheNightCrawler.items import parsedItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import re, time, random
from bumblebee import Keyboard

keyboard = Keyboard()
keyboard.set_typo_rate(random.randint(1, 3))  # 1-3% typo rate

JS_RECURSIVE_FINDER = """
function findAllElementsInShadowDOM(el, selector) {
    let elements = [];

    // 1. Find all matching elements in current element
    const currentElements = el.querySelectorAll ? el.querySelectorAll(selector) : [];
    elements.push(...currentElements);

    // 2. Check Shadow Root
    if (el.shadowRoot) {
        const shadowElements = findAllElementsInShadowDOM(el.shadowRoot, selector);
        elements.push(...shadowElements);
    }

    // 3. Recursively check all children
    const children = el.children || [];
    for (const child of children) {
        const childElements = findAllElementsInShadowDOM(child, selector);
        elements.push(...childElements);
    }

    return elements;
}

return findAllElementsInShadowDOM(arguments[0], arguments[1]);
"""

def typingInput(text):
    # Randomize typing parameters occasionally
    if random.random() < 0.3:  # 30% chance to adjust settings
        keyboard.set_speed(random.randint(85, 105))
        keyboard.set_consistency(random.randint(70, 90))
    keyboard.type(text)
    time.sleep(random.uniform(0.2, 0.5))

def ExecutingHTMLElement(method, value, elementType, browser, spider, inputValue="", timeout=10, elementName="", headless=False):
    spider.logger.info(f"Interacting with {elementName}")
    try:
        element = WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((method, value)))
        if elementType == "button":
            element.click()
            return "SUCCESS"
        elif elementType == "input field":
            element.click()
            if headless:
                element.send_keys(inputValue)
            else:
                typingInput(inputValue)
            return "SUCCESS"
        else:
            return element
    except TimeoutException:
        spider.logger.error(f"Cannot locate {elementName} - TimeoutException")
        shadowDOM = True
    except NoSuchElementException:
        spider.logger.error(f"Cannot locate {elementName} - NoSuchElementException")
        shadowDOM = True
    if shadowDOM:
        spider.logger.info(f"Attempting to locate {elementName} in shadow DOM")
        body = browser.find_element(By.TAG_NAME, 'body')
        element = browser.execute_script(JS_RECURSIVE_FINDER, body, value)
        if isinstance(element, WebElement):
            if elementType == "button":
                element.click()
                return "SUCCESS"
            elif elementType == "input field":
                element.click()
                if headless:
                    element.send_keys(inputValue)
                else:
                    typingInput(inputValue)
                return "SUCCESS"
            else:
                return element
        else:
            spider.logger.error(f"Cannot locate {elementName} in shadow DOM")
            return "FAIL"
    return "FAIL"


def scrollToBottom(lastHeight, browser):
    browser.execute_script("window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });")
    time.sleep(random.uniform(1, 2.5))  # Add human-like delay after scrolling
    newHeight = browser.execute_script("return document.documentElement.scrollHeight")
    if newHeight == lastHeight:
        return "Maximum Depth Reached"
    else:
        return newHeight

class NightCrawlerSpider(scrapy.Spider):
    name = "TheNightCrawler"
    allowed_domains = []
    handle_httpstatus_list = range(400, 500)

    def start_requests(self):
        URLS = {
            "CloudFare Enforced Sites": ["https://www.udemy.com/",
                                        "https://www.sofi.com/",
                                        "https://www.connectwise.com/",
                                        "https://www.delta.com/",
                                        "https://www.colliers.com/",
                                        "https://www.airtahiti.com/",
                                        "https://chatgpt.com/",
                                        "https://pos.toasttab.com/",
                                        "https://www.eon.com/",
                                        "https://www.crowe.com/",
                                        "https://www.lego.com/",
                                        "https://www.web.com/",
                                        "https://www.cummins.com/",
                                        "https://www.researchgate.net/",
                                        "https://www.abbvie.com/",
                                        "https://grok.com",
                                        "https://claude.ai/new"], # VERIFIED ALL TURNSTILE!

            "GOOGLE CAPTCHA Enforced Sites": ["https://jobs.experian.com/jobs",
                                         "https://rtcamp.com/",
                                         "https://www.amp.com.au/",
                                         "https://www.amtrak.com/home",
                                         "https://www.axi.com/int",
                                         "https://www.cardinalhealth.com/en.html",
                                         "https://www.cvent.com/",
                                         "https://www.interface.com/US/en-US.html",
                                         "https://www.moodys.com/",
                                         "https://www.sierrawireless.com/",
                                         "https://www.slb.com/",
                                         "https://www.travelers.com/",
                                         "https://www.weber.com/US/en/home/",
                                         "https://www.cookieyes.com/"], # VERIFIED ALL INVISIBLE!

            "HCAPTCHA Enforced Sites": ["https://www.veeam.com/",
                                        "https://www.riotgames.com/en",
                                        "https://www.shopify.com/login",
                                        "https://dashboard.stripe.com/login",
                                        "https://www.epicgames.com/id/login",
                                        "https://store.steampowered.com/join"], # VERIFIED ALL INVISIBLE!

            "MTCAPTCHA Enforced Sites": ["https://www.bader.at/meinbader/anmeldung", # Bader Registration Endpoint
                                         "https://www.goyard.com/us_en/customer/account/create/referer/", # Goyard Registration Endpoint
                                         "https://www.monamoda.nl/mijnaccount/aanmelding", # Monamoda Registration Endpoint
                                         "https://www.klingel.nl/mijnaccount/aanmelding", # Klingel Registration Endpoint
                                         "https://www.ghd.com/en/contact-us", # GHD Contact Endpoint
                                         "https://www.brigitte-salzburg.at/meinkonto/anmeldung", # Brigitte Registration Endpoint
                                         "https://amperecomputing.com/auth/register", # Ampere Computing Registration Endpoint
                                         "https://edpuzzle.com/",
                                         "https://admin.mtcaptcha.com/signup/profile?plantype=A"], # VERIFIED ALL USING MTCAPTCHA!

            "ALTCHA Enforced Sites": ['https://www.maximiles.com/',
                                      'https://www.qcitymetro.com/'], # VERIFIED ALL INVISIBLE!

           "Blue Team Sites": ['https://d1t82viux2kxdr.cloudfront.net/']
        }
        for category in URLS:
            self.logger.info("\n\n")
            self.logger.info("=" * 40)
            self.logger.info(f"CRAWLING WEBSITES IN CATEGORY {category}\nTotal: {len(URLS[category])} URLS")
            self.logger.info("=" * 40)
            self.logger.info("\n\n")
            for url in URLS[category]:
                yield scrapy.Request(url=url, callback=self.parse, meta={'use_selenium': True, 'selenium_wait_time': 30, 'use_mobile_headers': True, 'headless': False})

    def parse(self, response):
        self.logger.info(f'Parsing URL: {response.url}')
        self.logger.info(f'Status Code: {response.status}')
        self.logger.info(f'Response length: {len(response.text)} chars')
        browser = response.meta.get('selenium_browser')

        domainNamePattern = re.compile(r"(?:www\.)?([a-zA-Z0-9])+(?:\.[a-zA-Z0-9]+){1,12}")
        match = domainNamePattern.search(response.url)
        if match:
            fileName = match.group().replace("www.", "").replace(".com", "").replace(".", "")
        else:
            fileName =  str(random.randint(1, 300))

        captcha = ""

        if response.url.startswith("https://www.riotgames.com/"):
            loginButtons = browser.find_elements(By.CSS_SELECTOR, "a[data-riotbar-link-id='login']")
            for loginButton in loginButtons:
                try:
                    loginButton.click()
                except ElementNotInteractableException:
                    pass
            responseContent = browser.page_source
            browser.save_screenshot(f"{fileName}.png")
        elif response.url.startswith("https://d1t82viux2kxdr.cloudfront.net/"):
            browser.maximize_window()
            time.sleep(4)
            self.logger.info("Taking the screenshot of the page before filling out the form")
            browser.save_screenshot("InitialPage.png")
            ExecutingHTMLElement(By.CSS_SELECTOR, "input[name='firstName']", "input field", browser, self, inputValue="Sai", elementName="First Name Input Field", headless=response.meta.get('headless', False))
            ExecutingHTMLElement(By.CSS_SELECTOR, "input[name='lastName']", "input field", browser, self, inputValue="Gudapati", elementName="Last Name Input Field", headless=response.meta.get('headless', False))
            ExecutingHTMLElement(By.CSS_SELECTOR, "input[name='emailId']", "input field", browser, self, inputValue="SaiHairCut@gmail.com", elementName="Email Input Field", headless=response.meta.get('headless', False))
            ExecutingHTMLElement(By.CSS_SELECTOR, "textarea[name='text']", "input field", browser, self, inputValue="Sai has three biomes on his head and the proof of Global Warming", elementName="Message Input Field", headless=response.meta.get('headless', False))
            self.logger.info("Taking the screenshot of the page after filling out all the input fields in the form")
            browser.save_screenshot("InputAllFilled.png")
            ExecutingHTMLElement(By.CSS_SELECTOR, "button[type='submit']", "button", browser, self, elementName="Send Button")
            time.sleep(2)
            self.logger.info("Taking the screenshot of the page after clicking the send button")
            browser.save_screenshot("SendButtonClicked.png")
            status = ExecutingHTMLElement(By.CSS_SELECTOR, "input[type='checkbox']", "button", browser, self, elementName="Check Box Button")
            if status == "SUCCESS": # If we can locate the present of the checkbox, then we failed the invisible check!
                captcha = "BLUE TEAM VISIBLE CAPTCHA"
                self.logger.info("CAPTCHA check box detected and clicked, invisible CAPTCHA did not bypassed!")
                self.logger.info("Taking the screenshot of the page IF we got a CAPTCHA pop-up and clicked on the I'm not a robot")
                browser.save_screenshot("CAPTCHACheckBoxPressed.png")
                buttons = browser.find_elements(By.CSS_SELECTOR, "button[type='submit']")
                for button in buttons:
                    if button.text == "Continue":
                        button.click()
                time.sleep(2)
                self.logger.info("Taking the screenshot of the page after the CAPTCHA pop-up is resolved")
                browser.save_screenshot("FormSubmitted.png")
            else:
                captcha = "BLUE TEAM INVISIBLE CAPTCHA"
                self.logger.info("CAPTCHA check box did not detect, invisible CAPTCHA bypassed!")
            responseContent = browser.page_source
        else:
            responseContent = browser.page_source
            browser.maximize_window()
            browser.save_screenshot(f"{fileName}.png")
        fileName = f"{fileName}.html"
        with open(fileName, "w") as f:
            f.write(responseContent)
        self.logger.info(f"Response HTML for URL {response.url}written to file {fileName}")

        if not captcha:
            self.logger.warning("\n\n")
            self.logger.warning("=" * 40)
            self.logger.warning(f'URL: {response.url}')
            self.logger.warning("Checking for CAPTCHA vendor")
            self.logger.warning("=" * 40)
            self.logger.warning("\n\n")

            try:
                HTMLbody = browser.find_element(By.TAG_NAME, 'body')
                self.logger.info("Getting all iframe tags")
                iframes = browser.find_elements(By.TAG_NAME, 'iframe')
                self.logger.info("Getting all iframe tags in shadow DOMS")
                shadowDOMiframes = browser.execute_script(JS_RECURSIVE_FINDER, HTMLbody, "iframe")
                self.logger.info("Getting all script tags")
                scripts = browser.find_elements(By.TAG_NAME, 'script')
                self.logger.info("Getting all script tags in shadow DOMS")
                shadowDOMscripts = browser.execute_script(JS_RECURSIVE_FINDER, HTMLbody, "script")
                if not isinstance(iframes, list):
                    iframes = [iframes] if isinstance(iframes, WebElement) else []
                if not isinstance(scripts, list):
                    scripts = [scripts] if isinstance(scripts, WebElement) else []
                iframesAndScripts = iframes + shadowDOMiframes + scripts + shadowDOMscripts
            except Exception as error:
                self.logger.error(f"ERROR WHILE PARSING IFRAME AND SCRIPT SRCS: {error}")
                iframesAndScripts = []

            """Checking ALTCHA CAPTCHA"""
            try:
                ALTCaptcha = browser.find_element(By.TAG_NAME, 'altcha-widget')
                style = ALTCaptcha.get_attribute("style").lower()
                if ALTCaptcha.get_attribute("auto") in ['onload', 'onsubmit', 'onfocus'] or 'display: none' in style or 'visibility: hidden' in style:
                    captcha = "Non-intrusive ALTCHA Captcha"
                else:
                    captcha = "Standard ALTCHA Captcha"
            except NoSuchElementException:
                captcha = ""

            for element in iframesAndScripts:

                """Locating MTCaptchaConfig in the script or iframe innerHTML"""
                MTCaptchaConfig = element.get_attribute('innerHTML')
                if "mtCaptchaConfig" in MTCaptchaConfig:
                    captcha = "MTCAPTCHA in inner HTML"
                else:
                    src = element.get_attribute('src')
                    # Checking CloudFare Turnstile
                    if src.startswith(("https://challenges.cloudflare.com/cdn-cgi/challenge-platform/", "https://challenges.cloudflare.com/turnstile")):
                        captcha = "CLOUDFARE TURNSTILE CAPTCHA"

                    # Checking HCAPTCHA
                    elif src.startswith(("https://newassets.hcaptcha.com/captcha/v1/", "https://assets.hcaptcha.com/captcha/v1", "https://cf-assets.hcaptcha.com/captcha/v1")):
                        if "frame=checkbox-invisible" in src or "size=invisible" in src:
                            captcha = "Invisible HCAPTCHA CAPTCHA"
                        else:
                            try:
                                hCaptchaDiv = browser.find_element(By.CSS_SELECTOR, "div[class='h-captcha']")
                                invisible = hCaptchaDiv.get_attribute('data-size')
                                if invisible:
                                    if "invisible" in invisible:
                                        captcha = "Invisible HCAPTCHA CAPTCHA"
                                else:
                                    captcha = "Passive HCAPTCHA CAPTCHA"
                            except NoSuchElementException:
                                captcha = "Passive HCAPTCHA CAPTCHA"
                    elif src.startswith("https://js.hcaptcha.com/1/api.js"):
                        if "render=explicit" in src:
                            captcha = "Invisible HCAPTCHA CAPTCHA"
                        else:
                            captcha = "Passive HCAPTCHA CAPTCHA"

                    # Checking Google CAPTCHA
                    elif src.startswith("https://www.google.com/recaptcha/api2/"):
                        if "size=invisible" in src:
                            captcha = "Invisible Google V2 CAPTCHA"
                        else:
                            captcha = "Google V2 CAPTCHA"
                    elif src.startswith("https://www.google.com/recaptcha/api.js"):
                        if "render=explicit" in src:
                            captcha = "Google V2 with Check Box (Could Trigger Visible or Invisible) CAPTCHA"
                        elif src == "https://www.google.com/recaptcha/api.js" or "size=normal" in src:
                            captcha = "Google V2"
                        else:
                            captcha = "Invisible Google V3 CAPTCHA"
                    elif src.startswith("https://www.google.com/recaptcha/enterprise"):
                        captcha = "Google Enterprise CAPTCHA (Invisible)"

                    # Checking MTCAPTCHA
                    elif src.startswith("https://service.mtcaptcha.com/mtcv1/"):
                        display = element.get_attribute('style')
                        if display:
                            if "display: none" in display:
                                captcha = "Low-Friction MTCAPTCHA"
                            else:
                                captcha = "Active Challenge MTCAPTCHA"
                        else:
                            captcha = ""
                if captcha:
                    break

            if not captcha:
                """Checking for MTCaptchaConfig through global variables"""
                MTCaptchaConfig = browser.execute_script("return window.mtcaptchaConfig;")
                if MTCaptchaConfig:
                    if MTCaptchaConfig.get("lowFrictionInvisible", "") is True:
                        captcha = "Low-Friction MTCAPTCHA"
                    elif MTCaptchaConfig.get("loadAnimation", "") == "false" or MTCaptchaConfig.get("autoFormValidate", "") is True:
                        if MTCaptchaConfig.get("widgetSize", "") == "invisible":
                            captcha = "Low-Friction MTCAPTCHA"
                        else:
                            captcha = "Semi-Invisible MTCAPTCHA (Login or Sensitive PII endpoints will most likely visible CAPTCHA)"
                    else:
                        captcha = "Low-Friction MTCAPTCHA"
            if captcha:
                self.logger.warning("\n\n")
                self.logger.warning("=" * 40)
                self.logger.warning(f"{captcha} DETECTED for URL {response.url}")
                self.logger.warning("=" * 40)
                self.logger.warning("\n\n")
            else:
                if response.status in [403, 444]:
                    self.logger.warning("\n\n")
                    self.logger.warning("=" * 40)
                    self.logger.warning(f"NO CAPTCHA DETECTED for URL {response.url}, receiving status code {response.status} hinted website block")
                    self.logger.warning("=" * 40)
                    self.logger.warning("\n\n")
                    captcha = "HARD BLOCK BY WEBSITE"
                else:
                    self.logger.warning("\n\n")
                    self.logger.warning("=" * 40)
                    self.logger.warning(f"NO CAPTCHA DETECTED for URL {response.url}")
                    self.logger.warning("=" * 40)
                    self.logger.warning("\n\n")
                    captcha = "NO CAPTCHA DETECTED"

        self.logger.info("\n\n")
        self.logger.info("=" * 40)
        self.logger.info(f"CSV LOG FOR URL: {response.url}")
        self.logger.info("=" * 40)
        self.logger.info("\n\n")
        yield parsedItem(
            URL=response.url,
            CAPTCHATYPE=captcha,
            StatusCode=response.status,
            ContentLength=len(response.text),
        )
        if response.status == 200:
            # DO SOME SCRAPING HERE...
            pass
        self.logger.info(f"CLOSING BROWSER SESSION FOR: {response.url}")
        browser.quit()
