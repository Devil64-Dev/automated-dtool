from lxml import html
from lxml import etree
import re
"""A extractor obtain data from webpage source and return it"""
from utils.devil_dl.extractor.common import InfoExtractor
from utils.devil_dl.utils import (
    ExtractorError, int_or_none, url_or_none
)


class PlatziExtractor:
    def __init__(self, logger, page_source: str):
        """
        Extract information from platzi.com source page code
        :param logger:
        :param page_source:
        """
        self.logger = logger
        self.page_source = page_source
        self.__data = {}

        """
            __data structure:
            {
                'key': {
                    'path': 'target_path',
                    'use_file': Bool,  # if is set to true, path value will be used to file name
                    'download': [{'name': 'url'}, {}],  # download all items in this path, no required
                    'items': [[group1], [group2]], is file is set to true, the program, will be
                                                                skip 'download' and search all data here,
                                                                each dict is considered a set, each set is
                                                                separated using a line filled with '-' char.
                }
                'video': {
                    This is special, whe extractor detects this key, it will pass the data to youtube-dl
                    'serverA': {},
                    'serverX': {}
                }
            }
        """

    def __extract_data(self, key, path,  domain='', item_domain=None, patterns=None, use_file=False):
        """
        Extract real data from page source, a data stored in __data must be a dict and each value must be
        a html.Element.

        :param key: __data key
        :param path: storage place
        :param domain: base for incomplete links
        :param item_domain: number of element to add domain
        :param patterns: xpath expressions to search data
        :param use_file: type of file, False=save data in folder, True=save data into text file
        :return:
        """

        temp_data = {
            'path': path,
            'use_file': use_file,
            'download': [],
            'items': []
        }
        # extract data for each element
        for element in self.__data[key]:
            # data mus be wrote into text file or no?
            if use_file:
                data = []
                count = 0
                # extract data from element using all patterns
                for name, pattern in patterns.items():
                    try:
                        item = element.xpath(pattern)[0]
                        # print data to console
                        if isinstance(item_domain, int):
                            if count == item_domain:
                                item = domain + item
                                self.logger.log(f"\t + {name}: {item}")
                        else:
                            self.logger.log(f"\t + {name}: {item}")
                        if count == len(patterns) - 1:
                            print()

                        # if all is done, add data to list
                        data.append(name + ': ' + item)
                    except IndexError:
                        # pattern not found
                        self.logger(f"Error finding element: {name}")
                    count += 1

                # doman must be added to obtained data?

                # add a separator to data
                data.append(('-' * 100) + '\n')
                # add extracted data
                temp_data['items'].append(data)
            else:
                # data will be downloaded into folder
                # for this no need extra information, just url and file name
                try:
                    url = element.xpath('@href')[0]  # get url
                except IndexError:
                    self.logger.warning("Error loading URL.")
                    continue
                try:
                    name = element.xpath('@download')[0]  # get name
                    if len(name) < 3:
                        name = url.split('/')[-1]
                except IndexError:
                    # load name from url
                    self.logger.warning("")
                    name = url.split('/')[-1]

                # print results
                self.logger.log(f"\t + File URL: {url}")
                self.logger.log(f"\t + File name: {name}\n")

                # add extracted data
                temp_data['download'].append({'name': name, 'url': url})

            self.__data[key] = temp_data  # save data in __data

        # print place where data will be stored
        if use_file:
            self.logger.log(f"\tSave file name: {temp_data['path']}\n")
        else:
            self.logger.log(f"\tDownload path: {temp_data['path']}\n")

    def __print_data(self):
        for values in self.__data.values():
            if values['use_file']:
                # search in items
                for items in values['items']:
                    for item in items:
                        self.logger.log('\t' + item)
                        with open('example.txt', 'a') as f:
                            f.write(item + '\n')
            else:
                for item in values['download']:
                    self.logger.log(f"\tName: {item['name']}")
                    self.logger.log(f"\tURL: {item['url']}\n")

    def extract_video_urls(self):
        pass

    def extract_resources(self):
        """
        Extract data from resources such as files, links etc, this load page source and
        execute all code in this function, this must be returns a dict with data or bool

        :return:
        """

        self.logger.task("Searching for lesson resources.")
        element = '//div[@class="Resources"]'

        try:
            resources = html.fromstring(self.page_source)
        except TypeError:
            self.logger.error("Unable to load page content")
            self.logger.warning("Skipping resource extraction")
            return False

        try:
            resources = resources.xpath(element)[0]
        except IndexError:
            self.logger.info("No resources found for this lesson.")
            return True

        # recommended classes
        element = 'div/div[@class="RecommendedClasses-grid"]/a'
        if self.__extract('recommended_classes', element, resources):
            self.logger.line(spaces=2)
            self.logger.info("Found recommended classes, adding to extract list")
            patterns = {
                'Course': 'div/div/p[@class="RecommendedClasses-card--text"]/text()',
                'Class name': 'div/p[@class="RecommendedClasses-card--title"]/text()',
                'Class link': '@href'
            }
            self.__extract_data(
                'recommended_classes', 'recommended_classes.txt',
                domain='https://platzi.com', item_domain=2, patterns=patterns, use_file=True)
        else:
            self.logger.info("No recommended classes found")

        # files and links
        # files
        element = 'div[@class="FilesAndLinks"]/div[1]/a'
        if self.__extract('files', element, resources):
            self.logger.line(spaces=2)
            self.logger.info("Found lesson files, adding to extract list")
            self.__extract_data('files', 'files')

        else:
            self.logger.info("No lesson files found")

        # links
        element = 'div[@class="FilesAndLinks"]/div[2]/a'
        if self.__extract('lectures', element, resources):
            self.logger.line(spaces=2)
            self.logger.info("Found lesson lecture links, adding to extract list")
            patterns = {
                'Name': 'div/div/p[1]/text()',
                'URL': '@href'
            }
            self.__extract_data('lectures', 'lectures.txt', patterns=patterns, use_file=True)
        else:
            self.logger.info("No lesson lecture links found.")

    def get_data(self):
        self.extract_resources()

        if self.__data:
            return self.__data
        else:
            return False

    def __extract(self, key, element, tree):
        """
        Takes a xpath expression and search this in html.Element object, the result
        must be a iterable that is stored in self.__extract_data

        :param key: Dict key for result
        :param element: Xpath expression
        :param tree: html.Element or etree.Element
        :return: bool, process state
        """
        try:
            self.__data[key] = tree.xpath(element)
            if self.__data[key]:
                return True
            else:
                self.__data.pop(key)
                return False
        except etree.XPathEvalError:
            self.logger.warning(f"Invalid xpath pattern: {element}")
            return False

    @staticmethod
    def validate(url):
        __VALID_URL = r".*?platzi.com\/(clases|classes)/\d*-.*?\/\d*"
        try:
            if re.search(__VALID_URL, url).group():
                return True
        except AttributeError:
            return False


class PlatziIE(InfoExtractor):
    __NETRC_MACHINE = 'platzi'

    def __init__(self, page_source):
        super().__init__()
        self.page_source = page_source

    _VALID_URL = r'''(?x)
                    https?://
                        (?:
                            platzi\.com/clases|           # es version
                            courses\.platzi\.com/classes  # en version
                        )/[^/]+/(?P<id>\d+)-[^/?\#&]+
                    '''

    def _real_extract(self, url):
        lecture_id = url
        webpage = self.page_source
        if isinstance(webpage, str):
            data = self._parse_json(
                re.search(r"{\"courseDescription\".*?}}.*?\"courseTitle\".+?}", webpage).group(),
                lecture_id)
            material = data
            title = material['name']
            servers = material['video']['servers']
            formats = []
            for server_id, server in servers.items():
                if not isinstance(server, dict):
                    continue
                if "serverC" in servers:
                    if not server_id == "serverC":
                        continue
                for format_id in ('hls', 'dash'):
                    format_url = url_or_none(server.get(format_id))
                    if not format_url:
                        continue
                    if format_id == 'hls':
                        formats.extend(self._extract_m3u8_formats(
                            format_url, lecture_id, 'mp4',
                            entry_protocol='m3u8_native', m3u8_id=format_id,
                            note='Downloading %s m3u8 information' % server_id,
                            fatal=False
                        ))
                    elif format_id == 'dash':
                        formats.extend(self._extract_mpd_formats(
                            format_url, lecture_id, mpd_id=format_id,
                            note='Downloading %s MPD manifest' % server_id,
                            fatal=False
                        ))
            self._sort_formats(formats)

            description = material['content']
            duration = int_or_none(material.get('duration'), invscale=60)
            return {
                'id': lecture_id,
                'title': title,
                'description': description,
                'duration': duration,
                'formats': formats
            }
        else:
            raise ExtractorError(
                'Webpage content is not valid', expected=True
            )

    def _get_subtitles(self, *args, **kwargs):
        pass

    def _get_automatic_captions(self, *args, **kwargs):
        pass

    def _mark_watched(self, *args, **kwargs):
        pass
