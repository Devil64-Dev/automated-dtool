import os
import re

from dtool.utils.downloader.resources import ResourceDownloader
from lxml import html
from lxml import etree


class PlatziExtractor:
    def __init__(self, logger, page_source, url=None):
        """
        Extract information from platzi.com source page code
        :param logger:
        :param page_source:
        """
        self.logger = logger
        self.page_source = page_source
        self.url = url
        self.__data = {}

        """
            __data structure:
            {
                'key': {
                    'path': 'target_path',
                    'use_file': Bool,  # if is set to true, path value will be used to file name
                    'download': [{'name': '', 'url', 'url'}, {}],  # download all items in this path, no required
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

    def _extract_data(self, key, path,  domain='', item_domain=None, patterns=None, use_file=False):
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
                        # if count == len(patterns) - 1:
                        #     print()

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
            self.logger.log(f"\n\tSave file name: {temp_data['path']}\n")
        else:
            self.logger.log(f"\tDownload path: {temp_data['path']}\n")

    def _print_data(self):
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
        data = re.search(r'\{\"course')
        data = self._parse_json(
            re.search(r"{\"courseDescription\".*?}}.*?\"courseTitle\".+?}", self.page_source).group(),
            self.url)

        material = data
        title = material['name']
        servers = material["video"]["servers"]
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
                        format_url, lecture_selid, 'mp4',
                        entry_protocol='m3u8_native', m3u8_id=format_id,
                        note='Downloading %s m3u8 information' % server_id,
                        fatal=False))
                elif format_id == 'dash':
                    formats.extend(self._extract_mpd_formats(
                        format_url, lecture_id, mpd_id=format_id,
                        note='Downloading %s MPD manifest' % server_id,
                        fatal=False))
        self._sort_formats(formats)

        description = material['content']
        duration = int_or_none(material.get('duration'), invscale=60)
        print(formats)
        return {
            'id': lecture_id,
            'title': title,
            'description': description,
            'duration': duration,
            'formats': formats,
        }

    def extract_resources(self):
        """
        Extract data from resources such as files, links etc, this load page source and
        execute all code in this function, this must be returns a dict with data or bool

        :return:
        """

        self.logger.task("Searching for lesson resources.", start='\n')
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
        if self._extract('recommended_classes', element, resources):
            self.logger.line(spaces=2)
            self.logger.info("Found recommended classes, adding to extract list")
            patterns = {
                'Course': 'div/div/p[@class="RecommendedClasses-card--text"]/text()',
                'Class name': 'div/p[@class="RecommendedClasses-card--title"]/text()',
                'Class link': '@href'
            }
            self._extract_data(
                'recommended_classes', 'recommended_classes.txt',
                domain='https://platzi.com', item_domain=2, patterns=patterns, use_file=True)
        else:
            self.logger.info("No recommended classes found")

        # files and links
        # files
        element = 'div[@class="FilesAndLinks"]/div[1]/a'
        if self._extract('files', element, resources):
            self.logger.line(spaces=2)
            self.logger.info("Found lesson files, adding to extract list")
            self._extract_data('files', 'files')

        else:
            self.logger.info("No lesson files found")

        # links
        element = 'div[@class="FilesAndLinks"]/div[2]/a'
        if self._extract('lectures', element, resources):
            self.logger.line(spaces=2)
            self.logger.info("Found lesson lecture links, adding to extract list")
            patterns = {
                'Name': 'div/div/p[1]/text()',
                'URL': '@href'
            }
            self._extract_data('lectures', 'lectures.txt', patterns=patterns, use_file=True)
        else:
            self.logger.info("No lesson lecture links found", end='\n\n')

        return True

    def get_data(self):
        if not self.extract_resources():
            return False

        if self.__data:
            return self.__data
        else:
            return False

    def _extract(self, key, element, tree):
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


class DataExtractor:
    
    def __init__(self, settings, logger, url=None, browser=None, page_source=None):
        self.url = url
        self.browser = browser
        self.settings = settings
        self.logger = logger
        self.page_source = page_source
        self.__data = {
            'is_course': True,
            'name': '',
            'course_data': [],
            'route_data': []
        }
        self.type = None

        # __data structure
        """data = {
            'is_course': True|False,
            'course_name': 'Name', # only is_curse=True
            'route_data': [
                {
                    'course': 'Name',
                    'url': 'url',
                    'data': [
                        {
                            'section': 'Name',
                            'items': [
                                {
                                    'type': 'video|reading',
                                    'name': 'Name',
                                    'url': 'url',
                                }
                            ],
                        }, 
                        {
                            'section': 'Name',
                            'items': [
                                {
                                    'type': 'video',
                                    'name': 'name',
                                    'url': 'url'
                                }
                            ]
                        }
                    ]
                },
                {
                    'course': 'Name',
                    'url': 'url'
                }
            ]
        }"""

    def _extract_data(self):
        if os.path.exists("000 - Preview.html") and self.page_source is None:
            with open("000 - Preview.html", "r") as f:
                self.page_source = f.read()
                self.url = "Route data taken from local file."
        try:
            if self._load_webpage():
                if self.type == 'course':
                    self._extract_course_data()
                else:
                    self._extract_route_data()

                if len(self.__data['course_data']) > 0:
                    return True
                elif len(self.__data['route_data']) > 0:
                    return True
                else:
                    return False
            else:
                return False
        except KeyboardInterrupt:
            self.logger.error("Keyboard interrupt, finishing...")
            return False

    def _load_webpage(self):
        # https://platzi.com/clases/programacion-basica
        # https://platzi.com/idioma-ingles
        
        if self.page_source is None:
            try:
                re.search("https.*?clases.*?", self.url).group()
                self.logger.info("The URL will be take as (Single course) URL.")
            except AttributeError:
                self.logger.info("The URL will be taken as (Route) URL.")
            if self.browser.get(self.url):
                # check
                try:
                    re.search("<title>.*?>", self.browser.page_source).group()
                    self.page_source = self.browser.page_source

                except AttributeError:
                    self.logger.warning("Page content is not valid")
                    return False
            else:
                self.logger.error(f"Unable to load URL: {self.url}")
                return False
        self.url = "Information took from local file."

        try:
            re.search("<title>.*?>", self.page_source).group()
        except AttributeError:
            self.logger.error(f"Unable to load URL: {self.url}")
            return False

        tree = html.fromstring(self.page_source)
        pattern = '//div[@class="Material"]/div[@class="Material-concept"]'
        try:
            result = tree.xpath(pattern)[0]
            if len(result):
                pass
            self.type = 'course'
            return True
        except IndexError:
            # look for M
            pattern = '//div[@class="RoutesContent-content"]'
            try:
                result = tree.xpath(pattern)
                if len(result):
                    pass
                self.type = 'route'
                return True
            except IndexError:
                self.logger.error("The content of the page does not look like a course or route.")
                return False

    def _extract_course_data(self, counter='', url=None):
        page = html.fromstring(self.page_source)
        
        pattern = '//h1[@class="CourseDetail-left-title"]/text()'
        try:
            course_title = self._string_formatter(page.xpath(pattern)[0])
        except IndexError:
            self.logger.warning("Unable to extract course data")
            return False
        
        if not self.type == 'course':
            course_title = f"{counter} - {course_title}"

        # get main content
        pattern = '//div[@class="Material"]'
        material = page.xpath(pattern)[0]

        # get all sections
        pattern = 'div[@class="Material-concept"]'
        material = material.xpath(pattern)  # list
        
        # course title
        # start task
        self.logger.task("Extracting course data...", start='\n')
        self.logger.line()
        self.logger.log(f"    Course: {course_title}")
        
        sections_data = []
        section_number = 1
        lesson_number = 1
        for section in material:
            if not self.settings.global_numeration:
                lesson_number = 1

            if section_number > 9:
                sn = f"0{section_number} - "
            elif section_number > 99:
                sn = f"{section_number} - "
            else:
                sn = f"00{section_number} - "
            # title
            try:
                pattern = 'div/h3[@class="Material-title"]/text()'
                section_tile = sn + self._string_formatter(section.xpath(pattern)[0])
                current_section = {'name': section_tile, 'items': []}
                self.logger.log(f"      Section: {section_tile}")
            except IndexError:
                self.logger.warning("Error loading section data...")
                section_number += 1
                continue
            
            # lessons
            try:
                pattern = 'div[@class="MaterialItem-content"]'
                lessons = section.xpath(pattern)
            except IndexError:
                self.logger.warning("Error loading section content...")
                section_number += 1
                continue

            for lesson in lessons:
                if lesson_number > 9:
                    ln = f"0{lesson_number} - "
                elif lesson_number > 99:
                    ln = f"{lesson_number} - "
                else:
                    ln = f"00{lesson_number} - "

                try:
                    pattern = 'div/div/p[@class="MaterialItem-copy-title"]/text()'
                    lesson_title = ln + self._string_formatter(lesson.xpath(pattern)[0])
                    current_lesson = {'name': lesson_title}
                    self.logger.log(f"        Lesson: {lesson_title}")
                except IndexError:
                    self.logger.warning("Error loading lesson data..")
                    lesson_number += 1
                    continue

                temp = str(etree.tostring(lesson))
                pattern = r'\/clases\/[a-zA-Z0-9-]*\/\d*.*?/'
                try:
                    lesson_url = re.search(pattern, temp).group()
                    lesson_url = f"https://platzi.com{lesson_url}"
                    current_lesson['url'] = lesson_url
                    self.logger.log(f"        URL: {lesson_url}")
                except AttributeError:
                    self.logger.warning("Lesson is not available... skipping")
                    lesson_number += 1
                    continue

                try:
                    re.search('<div class=\"MaterialItem-vide.*?\"', temp).group()
                    current_lesson['type'] = 'video'
                    self.logger.log("        Type: Video")
                except AttributeError:
                    try:
                        re.search('<div class=\"MaterialItem-read.*?\"', temp).group()
                        current_lesson['type'] = 'reading'
                        self.logger.log("        Type: Reading")
                    except AttributeError:
                        current_lesson['type'] = 'unknown'
                        self.logger.warning("      Lesson type unknown, it will be download as webpage if is possible")
                self.logger.line(' ')
                current_section['items'].append(current_lesson)
                lesson_number += 1
            section_number += 1
            sections_data.append(current_section)
            self.logger.line(spaces=6, end='\n\n')

        if self.type == 'course':
            self.__data['name'] = course_title
            self.__data['url'] = self.url
            self.__data['is_course'] = True
            self.__data['course_data'] = sections_data
        else:
            course_data = {'name': course_title, 'url': url or self.url, 'data': sections_data}
            self.__data['is_course'] = False
            self.__data['route_data'].append(course_data)

        return True
    
    def _string_formatter(self, original):
        """
        Returns a string that only contains english alphabet

        :param original: Original string
        :return: formatted_str: str, formatted string,
        with special character of spanish language
        """

        # All know characters that no are valid for strings

        formatted_str = original  # value to work

        for par in self.settings.CHAR_EXCHANGE:
            if par['bad'] in formatted_str:
                # Replace 'bad' char with 'good' char
                formatted_str = formatted_str.replace(par['bad'], par['good'])

        # if formatted_str ends with "." remove them
        if formatted_str[len(formatted_str) - 1] == ".":
            formatted_str = formatted_str[:len(formatted_str) - 1]

        # if formatted_str end with " " remove them
        if formatted_str[len(formatted_str) - 1] == " ":
            formatted_str = formatted_str[:len(formatted_str) - 1]

        if "\t" in formatted_str:
            formatted_str = formatted_str.replace("\t", "")

        return formatted_str

    def _extract_route_data(self):
        page = html.fromstring(self.page_source)
        pattern = '//a[@class="RoutesList-item"]'
        course_list = page.xpath(pattern)
        
        pattern = '//div[@class="Hero-route-title"]/h1/text()'
        try:
            title = self._string_formatter(page.xpath(pattern)[0])
            self.__data['name'] = title
        except IndexError:
            title = "[Route name not available]"

        self.logger.task(f"Extracting data of route: {title}", start='\n')
        self.logger.line("")
        
        if not len(course_list) > 0:
            self.logger.error("Page not looks like a (route/school) page... Finishing...")
            return False
        
        course_numeration = 1
        data = []
        for course in course_list:
            if course_numeration > 9:
                cn = f"0{course_numeration}"
            elif course_numeration > 99:
                cn = f"{course_numeration}"
            else:
                cn = f"00{course_numeration}"
            try:
                pattern = 'h4/text()'
                title = cn + ' - ' + self._string_formatter(course.xpath(pattern)[0])
            except IndexError:
                self.logger.warning("Course info not available, skipping...")
                continue
            
            try:
                pattern = '@href'
                url = 'https://platzi.com' + course.xpath(pattern)[0]
                self.url = url
            except IndexError:
                self.logger("Course info not available, skipping...")
                continue

            self.logger.log(f"    Course: {title}\n    URL: {url}\n Index: {course_numeration - 1}")
            data.append({'name': title, 'url': url, 'status': True})
            course_numeration += 1

        while True:
            try:
                self.logger.log("If you want, execute more than one, separate by ',' Example: 1, 2, 3", start="'\n")
                exclude_list = input("    > Select courses to exclude (Index): ")
                break
            except (KeyboardInterrupt, EOFError):
                result = self.logger.cancel("Cancel route extraction")
                if result:
                    return False
            
        if len(exclude_list) > 0:
            exclude_list = exclude_list.replace(' ', '')
            exclude_list = exclude_list.split(',')

            for digit in exclude_list:
                if digit.isdigit():
                    try:
                        data[int(digit)]['status'] = False
                        self.logger.warning(f"Excluding course: {data[int(digit)]['name']}")
                        self.logger.log(f"\t URL: {data[int(digit)]['url']}")
                    except IndexError:
                        continue
        
        course_numeration = 1
        for course in data:
            if course_numeration > 9:
                cn = f"0{course_numeration}"
            elif course_numeration > 99:
                cn = f"{course_numeration}"
            else:
                cn = f"00{course_numeration}"

            check_path = ResourceDownloader.check_target_path

            if check_path(course['name']):
                document_path = course['name'] + '/000 - Preview.html'
                if check_path(document_path):
                    with open(document_path, 'r') as f:
                        self.page_source = f.read()
                        if self._load_webpage():
                            self.type = 'route'
                            self._extract_course_data(cn, url="Data taken from local file.")
                        else:
                            self.logger.warning("Skipping...")
                        course_numeration += 1
                        continue
            
            self.page_source = None
            self.url = course['url']
            if self.browser is not None:
                if self._load_webpage():
                    self.type = 'route'
                    self._extract_course_data(cn)
                    course_numeration += 1
                else:
                    continue
            else:
                self.logger.error("Browser not initialized, finishing...")
                return False

    def process_data(self):
        if self._extract_data():
            return self.__data
        else:
            return False

