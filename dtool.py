#!usr/bin/python3

import os
import sys
import random

from dtool.utils.extractor.platzi import (
    DataExtractor,
    PlatziExtractor
)
from dtool.utils.settings import BrowserSettings
from dtool.utils.handler.dialogs import Logger
from dtool.utils.handler.browser import BrowserManager
from dtool.utils.handler.session import SessionManager
from dtool.utils.downloader.resources import ResourceDownloader

try:
    url = sys.argv[1]
except IndexError:
    raise SystemExit("Usage: automated-dtool https://example.com")

def extract(path, page_source):
    extractor = PlatziExtractor(logger, page_source)
    data = extractor.get_data()
    if not isinstance(data, dict):
        pass
    
    return data


settings = BrowserSettings(os.path.abspath(__file__))
logger = Logger(settings)

try:
    if not os.path.exists(os.path.abspath(__file__)[:-1] + '/.cache'):
        logger.info("Creating cache folder...")
        os.mkdir(os.path.abspath(__file__)[:-1] + '/.cache')
except FileExistsError:
    pass

session_manager = SessionManager(
    settings, 'platzi', logger=logger, site_url="https://platzi.com",
    login_url="https://platzi.com/login/"
    )

browser = BrowserManager(logger, settings, headless=True)
browser.call_browser()
browser = session_manager.start_session(browser)

if isinstance(browser, bool):
    browser.quit()
    logger.error("Error starting session. Exiting...")
    raise SystemExit()

data = DataExtractor(settings, logger, url=url, browser=browser)
data = data.process_data()
# os.system("clear")

logger.task("Loading resourses...")
logger.line()
if not isinstance(data, dict):
    browser.quit()
    exit()

if data['is_course']:
    logger.log(f"    Course: {data['name']}")
    logger.log(f"    URL: {data['url']}")
    for section in data['course_data']:
        for lesson in section['items']:
            os.system("clear")
            logger.log(f"    Section : {section['name']}")
            logger.log(f"      Name: {lesson['name']}")
            logger.log(f"      URL: {lesson['url']}")
            if lesson['type'] == 'video':
                dirs = [item for item in os.listdir() if os.path.isdir(item)]
                path = data['name']
                for dir in dirs:
                    normalize = dir[6:]
                    if normalize == data['name']:
                        path = dir
                        break
                    
                path += f"/{section['name']}/"
                path += f"{lesson['name'][:3]} - extra_files"
                settings.load_await = (random.randint(settings.load_await, settings.load_await + 10))
                if not browser.get(lesson['url']):
                    logger.warning("Unable to load lesson page. Skipping...")
                    continue
                with open('page.html', 'w') as f:
                    f.writelines(browser.page_source)
                # print(browser.page_source)
                resources = extract(path=path, page_source=browser.page_source)
                if isinstance(resources, dict):
                    downloader = ResourceDownloader(settings, logger, path, resources)
                    downloader.process_data()
                    downloader.webpage_download(f"{lesson['name'][:3]} - webpage.html", browser, lesson['url'], overwrite=True, download=False)
                else:
                    continue
else:
    route = data['route_data'] # courses
    for course in route:
        logger.log(f"    Course: {course['name']}")
        logger.log(f"    URL: {course['url']}")
        for section in course['data']: # course section
            for lesson in section['items']: # section lessons
                os.system("clear")
                logger.log(f"      Section: {section['name']}")
                logger.log(f"        Name: {lesson['name']}")
                logger.log(f"        URL: {lesson['url']}")
                logger.log(f"        Type: {lesson['type']}")
                if lesson['type'] == 'video':
                    dirs = [item for item in os.listdir() if os.path.isdir(item)]
                    path = course['name']
                    for dir in dirs:
                        normalize = dir[6:]
                        if normalize == data['name']:
                            path = dir
                            break
                    path += f"/{section['name']}/"
                    path += f"{lesson['name'][:3]} - extra_files"
                    if not browser.get(lesson['url']):
                        logger.warning("Unable to load lesson page. Skipping...")
                        continue
                    resources = extract(path=path, page_source=browser.page_source)
                    if isinstance(resources, dict):
                        downloader = ResourceDownloader(settings, logger, path, resources)
                        downloader.process_data()
                        downloader.webpage_download(f"{lesson['name'][:3]} - webpage.html", browser, lesson['url'], overwrite=True, download=False)

        os.system("clear")

browser.quit()