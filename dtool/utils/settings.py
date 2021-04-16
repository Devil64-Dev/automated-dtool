#!/usr/bin/python3
import os

"""
    In this file are stored all program settings such as
    times per browser page loading and youtube-dl time per downloads
    ant others
"""


class GeneralSetting:
    logger_times = {
        'NORMAL': 0.1,
        'SUCCESS': 0.5,
        'INFO': 0.3,
        'WARNING': 0.4,
        'ERROR': 0.5,
        'Task': 0.5
    }
    process_sleep = 1
    large_output_sleep = 0.4
    download_wait = 5

    # extractor
    # if True, section1 lessons{1, 2, 3}, section2 lessons{1, 2, 3}
    # if False, section1 lessons{1, 2, 3}, section2 lessons{4, 5, 6}
    global_numeration = True  


    WGET_EXIT_STATUS = {
        0: {'status': True, 'retry': False, 'message': ''},
        1: {'status': False, 'retry': False, 'message': "Generic error code"},
        2: {'status': False, 'retry': False, 'message': "Parse error—for instance, when parsing \
            command-line options, the ‘.wgetrc’ or ‘.netrc’..."},
        3: {'status': False, 'retry': False, 'message': "Error writing/reading file"},
        4: {'status': False, 'retry': True, 'message': "Network failure"},
        5: {'status': False, 'retry': True, 'message': "SSL verification failure"},
        6: {'status': False, 'retry': False, 'message': "Username/password authentication failure."},
        7: {'status': False, 'retry': False, 'message': "Server issued an error response"},
        8: {'status': False, 'retry': False, 'message': "Protocols error"},
        130: {'status': False, 'retry': False, 'message': "User"}

    }

    EXTENSIONS = ['.mp4', '.ts', '.webm', '.mkv', '.html']

     # All know characters that no are valid for strings
    CHAR_EXCHANGE = [{'bad': 'ó', 'good': 'o'}, {'bad': 'á', 'good': 'a'},
                  {'bad': 'é', 'good': 'e'}, {'bad': 'í', 'good': 'i'},
                  {'bad': 'ú', 'good': 'u'}, {'bad': ':', 'good': ' -'},
                  {'bad': '/', 'good': '__'}, {'bad': '¿', 'good': ''},
                  {'bad': 'Á', 'good': 'A'}, {'bad': 'É', 'good': 'E'},
                  {'bad': 'Í', 'good': 'I'}, {'bad': 'Ó', 'good': 'O'},
                  {'bad': 'Ú', 'good': 'U'}, {'bad': 'à', 'good': 'a'},
                  {'bad': 'è', 'good': 'e'}, {'bad': 'ì', 'good': 'i'},
                  {'bad': 'ù', 'good': 'ù'}, {'bad': 'À', 'good': 'A'},
                  {'bad': 'È', 'good': 'E'}, {'bad': 'Ì', 'good': 'I'},
                  {'bad': 'Ù', 'good': 'Ù'}, {'bad': '`', 'good': ''}]


class BrowserSettings(GeneralSetting):
    def __init__(self, parent):
        self.load_await = 10
        self.js_await = 10
        self.session_check_time = 10
        self.mode_change_time = 10
        self.cookies_path = '/'.join(parent.split('/')[:-1]) + '/.cache'
        self.connection_timeout_retry = 20
        self.messages = {
            1: "Browser is not active or initialized.",  # AttributeError
            2: f"Server communication error, retrying in {self.connection_timeout_retry}s.",  # ErrorInResponseException
            3: f"Connection timeout, retrying in {self.connection_timeout_retry}s.",  # TimeoutException
            4: "Webdriver error, unable to retry, closing browser.",  # WebdriverException
            5: "Unable to close browser, please do it manually with a task manager.",  # .quit() WebdriverException
            6: "No valid result was received.",  # Invalid response
            7: "Domain name no are same in the cookie file",  # InvalidCookieDomainException
            8: "Closing browser...",  # Fatal error
            9: "Unable to load cookies",  # Load cookies error
            10: "Please log in to the website and then press the ENTER key."  # Website logging
        }
        self.exit = "Exiting program..."


class YoutubeDLSettings(BrowserSettings):
    download_sleep_time = 10
