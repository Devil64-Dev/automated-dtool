# import utils.browser as browser_manager
# from time import sleep
import os
import re
import json

"""
    @author Devil64-Dev
    This module manager website access
"""


class SiteSession:

    def __init__(self, settings, name, logger, site_url, login_url=False, regex_pattern=None):
        """
        Handles sessions on a domain, this can load cookies to browser through BrowserManager object.

        :param logger: Logger object for output info
        :param site_url: Website domain
        :param login_url: URL used to perform login
        :param regex_pattern: Search this pattern in website to check access
        """

        self.settings = settings
        self.name = name
        self.logger = logger
        self.domain = site_url
        self.login_url = login_url
        self.regex = regex_pattern
        self.cookies = []
        self.cookie_name = settings.cookies_path + '/cookies-' + name

    def __check_access(self, browser, page_source=False):
        """
        Checks website access using a regex pattern, regex pattern is defined
        it will be passed so re.search, else this means that site not requieres login check

        :param browser: BrowserManager object
        :param page_source: String where self.regex will be searched
        :return: bool, Access state
        """
        if isinstance(self.regex, str):
            if isinstance(page_source, (str, tuple, list, bytes)):
                try:
                    self.logger.info("Checking access to website")
                    if re.search(self.regex, page_source).group():
                        self.logger.error("Access denied")
                        return False
                except AttributeError:
                    self.logger.success("Access granted")
                    return True
            else:
                self.logger.info(f"Loading {self.domain}")
                if browser.get(self.domain):
                    self.__check_access(browser, page_source=browser.page_source)
        else:
            self.logger.warning("Access check pattern not set")
            return True

    def __login(self, browser):
        """
        Perform login from a browser to get full access to the website,
        session is valid through regex search.
        If login is success, cookies data will be saved to -> self.cookies

        :return: bool, login result
        """
        if isinstance(self.login_url, str):
            self.logger.task(f"Logging on the website {self.domain}")
            self.logger.info(f"Loading login URL: {self.login_url}", end='\r')
            if browser.get(self.login_url):
                self.logger.success(f"L form loaded from the URL: {self.login_url}", end='\n\n')
                self.logger.info(self.settings.message[10], end='\r')
                input()
                if self.__check_access(browser, page_source=browser.page_source):
                    self.logger.success("Login correct")
                    return True
                else:
                    self.logger.error("Login incorrect")
                    return True
            else:
                return False

    def load_cookies(self, browser):
        """
        Restore saved cookies in cookies_path to browser through BrowserManager object

        :param browser: BrowserManager object
        :return: bool, Cookies load state
        """
        browser.add_cookies(self.cookies, self.domain)
        return browser

    def set_cookies_from_file(self, cookiefile=None):
        cookie_file = self.cookie_name
        if isinstance(cookiefile, str):
            cookie_file = cookie_file

        self.logger.info(f"Decoding cookies from file: {cookie_file.split('/')[-3]}")
        with open(cookie_file, 'r') as cookies:
            self.cookies = []
            for cookie in cookies.readlines():
                try:
                    self.cookies.append(json.loads(cookie))
                    try:
                        self.logger.info(f"Decoding cookie: {json.loads(cookie)['name']}", end='\r')
                    except KeyError:
                        self.logger.info(f"Decoding cookie: name_not_available", end='\r')

                except json.JSONDecodeError:
                    self.logger.warning("Cookie format is not valid. Skipping...")

            if len(self.cookies) > 1:
                self.logger.success(f"Cookies decoded from file {cookie_file.split('/')[-3]}")
                return True
            else:
                self.logger.warning(f"Cookie format error in file: {cookie_file}")
                return False

    def start_session(self, browser):
        if os.path.exists(self.cookie_name):
            if self.set_cookies_from_file():
                return self.load_cookies(browser)
            else:
                return False
