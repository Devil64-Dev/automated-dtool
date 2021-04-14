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
            self.logger.success("Browser launched.")
        except AttributeError:
            self.logger.info("Launching browser.", end='\r')
            driver = webdriver.Firefox(options=self.options)
            self.browser = driver
            self.logger.success("Browser launched.")

    def get(self, url):
        try:
            sleep(self.settings.load_await)
            self.browser.get(url)
            if self.javascript:
                sleep(self.settings.js_await)

            return True
        except TimeoutException:
            self.logger.error(self.settings.messages[3])
            sleep(self.settings.connection_timeout_retry)
            self.get(url)

        except ErrorInResponseException:
            self.logger.error(self.settings.messages[2])
            sleep(self.settings.connection_timeout_retry)
            self.get(url)

        except WebDriverException:
            self.logger.error(self.settings.messages[4])
            self.quit()

        return False

    @property
    def page_source(self):
        try:
            return str(self.browser.page_source)
        except AttributeError:
            self.logger.warning(self.settings.messages[1])
            return "<html></html>"
        except WebDriverException:
            self.logger.error(self.settings.messages[4])
            return "<html></html>"

    def quit(self):
        self.logger.info(self.settings.messages[8])
        try:
            self.browser.quit()
        except AttributeError:
            self.logger.warning(self.settings.messages[1])
            return True
        except WebDriverException:
            self.logger.error(self.settings.messages[5])
            self.browser.quit()
            return False

        self.browser.quit()
        return True

    def get_cookies(self):
        try:
            return self.browser.get_cookies()
        except AttributeError:
            self.logger.warning(self.settings.messages[1])
        except WebDriverException:
            self.logger.error(self.settings.messages[4])
        finally:
            return self.browser.get_cookies()

    def add_cookies(self, cookies, domain_url):

        self.get(domain_url)
        if isinstance(cookies, list):
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

            self.logger.success("Cookies restored.")
            return True
