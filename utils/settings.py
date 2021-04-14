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


class BrowserSettings(GeneralSetting):
    def __init__(self, parent):
        self.load_await = 10
        self.js_await = 10
        self.session_check_time = 10
        self.mode_change_time = 10
        self.cookies_path = '/'.join(os.path.abspath(parent).split('/')[:-1]) + '/.cache'
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
