#!/usr/bin/python3
import os
from utils.downloader.resources import ResourceDownloader
from utils.extractor.platzi import DataExtractor
from utils.handler.dialogs import Logger
from utils.extractor.platzi import PlatziExtractor
from utils.settings import BrowserSettings
import sys


page = ""

def print_data(data):

    if data['is_course']:
        print(f"Course name: {data['name']}")
        print(f"Course URL: {data['url']}")
        for section in data['course_data']:
            print(f"Section name: {section['name']}")
            for lesson in section['items']:
                print(f"Name: {lesson['name']}")
                print(f"Type: {lesson['type']}")
    else:
        route = data['route_data'] # courses
        for course in route:
            print(f'Name: {course["name"]}')
            print(f'URL: {course["url"]}')
            for section in course['data']: # course section
                print(f'Section: {section["name"]}')
                for lesson in section['items']: # section lessons
                    print(f"Name: {lesson['name']}")
                    print(f"Type: {lesson['type']}")


def __print_data(data, logger):
    for values in data.values():
        if values['use_file']:
            # search in items
            for items in values['items']:
                for item in items:
                    logger.log('\t' + item)
                    with open('example.txt', 'a') as f:
                        f.write(item + '\n')
        else:
            for item in values['download']:
                logger.log(f"\tName: {item['name']}")
                logger.log(f"\tURL: {item['url']}\n")


if __name__ == "__main__":
    settings = BrowserSettings(os.path.abspath(__file__))
    logger = Logger(settings)
    # browser = browser.BrowserManager(logger=logger, settings=settings, headless=True)
    # browser.call_browser()
    # login_url = "https://platzi.com/login/"
    # session = SiteSession(settings, 'platzi', logger=logger, site_url="https://platzi.com")
    # session.start_session(browser=browser)
    # url = "https://platzi.com/clases/1050-programacion-basica/5114-el-dom-nuestro-lugar-de-trabajo-en-la-web/"
    url = 'https://platzi.com/clases/programacion-basica/'
    """if not browser.get(url):
        browser.quit()
        exit()"""
    with open('page.html', 'r') as f:
        page = f.read()
    # browser.get(url)
    data = DataExtractor(settings, logger, url, page_source=page)
    
    # data._extract_data()
    # browser.quit()
    extractor = PlatziExtractor(logger=logger, page_source=page)
    re_handler = ResourceDownloader(settings, logger, 'test/files', extractor.get_data())
    re_handler.process_data(overwrite=False)

    #re_handler.webpage_download('page.html', browser, url, download=False)
    # browser.quit()
"""    with YoutubeDL(ydl_options) as ydl:
        url = 'https://mdstrm.com/video/5b2d272b5f744265f2277806.m3u8?access_token=EeqKSJNSemBgozOL0TOWE05MOonv0VFhsH5HbP6w4HNnzi8zjyffkfO5PQXrM3Ltto3QCi1WWQR'
        pe = ydl.get_info_extractor('Platzi')
        formats = pe._real_extract('https://platzi.com/clases/1249-dasas/2123-sassas')
        # print(formats)
        ydl.process_video_result(formats)
        formats.extend(pe.(
            url, 'platzi', 'mp4', entry_protocol='m3u8_native',
            m3u8_id='hls', note='Downloading serverC m3u8 information',
            fatal=False
        ))
        

        print(formats)
        info_dict = {
            'id': 'platzi',
            'title': 'test',
            'description': '',
            'duration': int_or_none(357, invscale=60),
            'formats': formats
        }
        ydl.process_info(info_dict)
        formats = pe._extract_m3u8_formats()url, 'platzi', 'mp4',
        entry_protocol='m3u8_native', m3u8_id='hls',
        note='Downloading serverC m3u8 information',
        fatal=False)) """

def print_data(data):

    if data['is_course']:
        print(f"Course name: {data['name']}")
        print(f"Course URL: {data['url']}")
        for section in data['course_data']:
            print(f"Section name: section['name']")
            for lesson in section['items']:
                print(f"Name: {lesson['name']}")
                print(f"Type: {lesson['type']}")
    else:
        route = data['route_data'] # courses
        for course in route:
            print(f'Name: {course["name"]}')
            print(f'URL: {course["url"]}')
            for section in course['data']: # course section
                print(f'Section: {section["name"]}')
                for lesson in section['items']: # section lessons
                    print(f"Name: {lesson['name']}")
                    print(f"Type: {lesson['type']}")
