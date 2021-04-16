import os
import sys
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


try:
    os.mkdir(os.path.abspath(__file__)[:-1])
except FileExistsError:
    pass


def extract(path, page_source):
    extractor = PlatziExtractor(logger, page_source)
    data = extractor.get_data()
    if not isinstance(data, dict):
        exit()
    
    return data


settings = BrowserSettings(os.path.abspath(__file__))
logger = Logger(settings)

session_manager = SessionManager(
    settings, 'platzi', logger=logger, site_url="https://platzi.com",
    login_url="https://platzi.com/login/"
    )

browser = BrowserManager(logger, settings, headless=True)
browser.call_browser()
if not isinstance(session_manager.start_session(browser), bool):
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
        logger.log(f"      Section : {section['name']}")
        for lesson in section['items']:
            logger.log(f"        Name: {lesson['name']}")
            logger.log(f"        URL: {lesson['url']}")
            logger.log(f"        Type: {lesson['type']}")
            if lesson['type'] == 'video':
                path = f"{data['name']}/{section['name']}/"
                path += f"{lesson['name'][:3]} - extra_files"
                if browser.get(lesson['url']):
                    logger.warning("Unable to load lesson page. Skipping...")
                    continue
                resources = extract(path=path, page_source=browser.page_source)
                if isinstance(resources, dict):
                    downloader = ResourceDownloader(settings, logger, path, resources)
                    downloader.process_data()

else:
    route = data['route_data'] # courses
    for course in route:
        logger.log(f"    Course: {course['name']}")
        logger.log(f"    URL: {course['url']}")
        for section in course['data']: # course section
            logger.log(f"      Section: {section['name']}")
            for lesson in section['items']: # section lessons
                logger.log(f"        Name: {lesson['name']}")
                logger.log(f"        URL: {lesson['url']}")
                logger.log(f"        Type: {lesson['type']}")
                if lesson['type'] == 'video':
                    path = f"{course['name']}/{section['name']}/"
                    path += f"{lesson['name'][:3]} - extra_files"
                if browser.get(lesson['url']):
                    logger.warning("Unable to load lesson page. Skipping...")
                    continue
                resources = extract(path=path, page_source=browser.page_source)
                if isinstance(resources, dict):
                    downloader = ResourceDownloader(settings, logger, path, resources)
                    downloader.process_data()

        os.system("clear")

browser.quit()