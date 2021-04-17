from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.errorhandler import (
    WebDriverException, TimeoutException,
    InvalidCookieDomainException, ErrorInResponseException
)
from time import sleep


class BrowserManager:
    def __init__(self, logger, settings, headless=False, javascript=True):
        self.options = Options()
        self.options.headless = headless
        self.javascript = javascript
        self.options.preferences.update({'javascript.enabled': self.javascript})
        self.browser = None
        self.logger = logger
        self.settings = settings

    def call_browser(self):
        try:
            self.browser.quit()
            self.logger.info("Launching browser.", end='\r')
            driver = webdriver.Firefox(options=self.options)
            self.browser = driver
            self.logger.info("Browser launched.")
        except AttributeError:
            self.logger.info("Launching browser.", end='\r')
            driver = webdriver.Firefox(options=self.options)
            self.browser = driver
            self.logger.info("Browser launched.")

    def get(self, url):
        try:
            try:
                sleep(self.settings.load_await)
                self.logger.info(f"Loading URL: {url}")
                self.browser.get(url)
                if self.javascript:
                    sleep(self.settings.js_await)

                return True

            except TimeoutException:
                self.logger.error(self.settings.messages[3])
                sleep(self.settings.connection_timeout_retry)
                self.get(url)

            except ErrorInResponseException as err:
                self.logger.error(self.settings.messages[2] + f'Info: {err}')
                sleep(self.settings.connection_timeout_retry)
                self.get(url)

            except WebDriverException as err:
                self.logger.error(self.settings.messages[4] + f'Info: {err}')
                return False

        except KeyboardInterrupt:
            result = self.logger.cancel(f"Cancel loading URL: {url}")
            if result:
                return False
            else:
                self.get(url)

    @property
    def page_source(self):
        result = self.browser.page_source
        if result is not None:
            return str(result)
        else:
            self.logger.warning("Webpage content is not valid")
            return "<html><head></head><body></body></html>"

    def quit(self):
        self.logger.info(self.settings.messages[8])
        try:
            self.browser.quit()
            return True
        except AttributeError:
            self.logger.warning(self.settings.messages[1])
            return True
        except WebDriverException:
            self.logger.error(self.settings.messages[5])
            self.browser.quit()
            return False
        except ConnectionRefusedError:
            return True

    def get_cookies(self):
        try:
            return self.browser.get_cookies()
        except AttributeError:
            self.logger.warning(self.settings.messages[1])
            return []
        except WebDriverException:
            self.logger.error(self.settings.messages[4])
            return []

    def add_cookies(self, cookies, domain_url):

        self.logger.info("Starting the restoration of cookies")
        if not self.get(domain_url):
            return False
        if isinstance(cookies, list) and len(cookies) > 2:
            try:
                for cookie in cookies:
                    try:
                        if 'name' in cookie:
                            self.logger.info(f"Restoring cookie: {cookie['name']}", end='\r')
                        else:
                            self.logger.info("Restoring cookie: name_not_available", end='\r')
                        self.browser.add_cookie(cookie)
                    except AttributeError:
                        self.logger.warning(self.settings.messages[1])
                        return False
                    except InvalidCookieDomainException:
                        self.logger.error(self.settings.messages[7])
                        self.logger.error(self.settings.messages[9])
                        return False

                    except WebDriverException:
                        self.logger.error(self.settings.messages[4])
                        self.quit()
                        return False
            except KeyboardInterrupt:
                self.logger.error('Keyboard interrupt received, ending program...')
                self.quit()
                return False

            self.logger.info("Cookies restored.", start='\n')
            return True
        else:
            self.logger.warning("No cookies to restore.")
            return False