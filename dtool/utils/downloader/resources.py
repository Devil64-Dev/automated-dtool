from io import FileIO
import os
import re
import subprocess

from time import sleep


class ResourceDownloader:
    
    def __init__(self, settings, logger, path, data):
        """
        Download any type of resources,
        """
        self.settings = settings
        self.logger = logger
        self.data = data
        self.path = path

    def process_data(self, overwrite=False):
        if isinstance(self.data, dict):
            for resource_key, resource_value in self.data.items():
                if resource_key == "videos":
                    continue
                
                if not resource_value['use_file']:
                    # download archives
                    if self._file_download_handler(resource_value['download'], overwrite=overwrite):
                        self.logger.success("Download complete successfully")
                    else:
                        self.logger.warning("Some files could not be downloaded")
                else:
                    if self._write_data(resource_value):
                        self.logger.success("Extra resources saved.")
                    else:
                        self.logger.warning("Unable to save extra resources")

            return True
        
        else:
            self.logger.warning("No resources found to save/download.")
            return True

    def _file_download_handler(self, items: list, retries=3, wait=7, overwrite=False):
        check_path = ResourceDownloader.check_target_path
        full_path = self.path
        if not '/' == self.path[-1]:
            full_path += '/'
        full_path += 'files'
        if not check_path(full_path, create=True, logger=self.logger):
            return False

        status = True
        is_retry = False
        parent_path = os.getcwd()
        download_path = os.path.abspath(full_path)
        self.logger.task("Downloading lesson files.", start='\n')
        for download_item in items:
            name = download_item['name']
            full_name = full_path + name
            self.logger.line('-', 2)
            if check_path(full_name):
                if overwrite:
                    self.logger.warning(f"File: {download_item['name']} already exists. Overwriting.")
                    os.remove(full_name)
                else:
                    self.logger.info(f"File: {download_item['name']} already exists.")
                    status = True
                    continue
            
            attempts = retries
            while attempts > 0:
                os.chdir(download_path)
                result = self._download(download_item['url'], name, is_retry=is_retry)
                is_retry = False
                os.chdir(parent_path)
                if result['status']:
                    self.logger.log("  Download complete", end='\n\n')
                    status = True
                    break
                else:
                    if result['retry']:
                        self.logger.warning(f"Download interrupted by: {result['message']}")
                        attempts -= 1
                        is_retry = True
                    else:
                        self.logger.warning(f"Download cancelled by: {result['message']}")
                        status = False
                        break
            else:
                self.logger("Maximum number of attempts achieved, skipping download.")
                status = False
            try:
                sleep(wait)
            except KeyboardInterrupt:
                result = self.logger.cancel("Cancel all downloads")
                if result:
                    return False
        
        return status

    def _download(self, url, name, is_retry=False, is_resume=False, retry_time=None):
        command = f'wget -q --show-progress --continue -O "{name}" "{url}"'

        download_head = "    Download information\n"
        sp = ' ' * 6
        download_body = f"{sp}Name: {name}\n{sp}URL: {url}\n"

        if is_resume:
            download_head = "    Resuming download..."
            download_body = ""
        elif is_retry:
            download_head = "    Retrying download..."
            if retry_time is not None:
                download_head += f"Remaining attempts {retry_time}"
            download_head += '\n'
            download_body = f"{sp}Name: {name}\n"

        STATUS_CODE = self.settings.WGET_EXIT_STATUS
        self.logger.log(f"{download_head + download_body}")

        try:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            result = result.returncode

            return STATUS_CODE[result]

        except KeyboardInterrupt:
            result = self.logger.cancel("Cancel download")
            if result:
                return STATUS_CODE[130]
            else:
                self._download(url, name, is_resume=True)
        except subprocess.TimeoutExpired:
            self.logger.warning("Download start timeout, retrying..")
            self._download(url, name, is_retry=True)

        return STATUS_CODE[result]  # if KeyboardInterrupt
    
    def _write_data(self, data):
        check_path = ResourceDownloader.check_target_path
        full_path = self.path

        if not '/' == self.path[-1]:
            full_path += '/'
        
        if not check_path(full_path, create=True):
            return False

        full_path += data['path']

        if check_path(full_path):
            self.logger.info("File already exists... Updating content...")
        self.logger.info(f"Writing data to: {full_path}")
        
        try:
            with open (full_path, 'w') as f:
                for group in data['items']:
                    for item in group:
                        f.write(item + '\n')
            return True
        except (IOError, FileNotFoundError):
            self.logger.error(f"Can't not save data to file: {full_path}")
            return False

    def webpage_download(self, name, browser, url, path=None, wait=6, overwrite=False, download=True):
        """
        Download a webpage using a BrowserManager object, if overwrite is set to True
        and the file exists will be overwrite with new file.

        :param browser: Requests (url) and handle content
        :param path: Folder to save file
        :param name: File name
        :param url: Requests URL
        :param wait: Default 5, sleep time after success download
        :param overwrite: Default False, overwrite file
        :param download: If set to true, webpage content is loaded from url

        :returns: (bool) Download state 
        """

        check_path = ResourceDownloader.check_target_path
        if path is None:
            path = self.path

        if check_path(path, create=True, logger=self.logger):
            if '/' == path[-1]:
                path += name
            else:
                path = f"{path}/{name}"

            if check_path(path, logger=self.logger):
                if not overwrite:
                    return True
        
        else:
            self.logger.error("Unable to download webpage")
            return False

        if download:
            self.logger.info("Downloading webpage from {url}")
            
            if not browser.get(url):
                self.logger.warning(f"Unable to load URL: {url}")
                return False
        try:
            re.search('<title>.*?>', browser.page_source).group()
        except AttributeError:
            self.logger.warning("Page content is invalid")
            return False

        self.logger.info(f"Saving page as {path}")
        try:
            with open(path, 'w') as f:
                f.write(browser.page_source)
            if download:
                sleep(wait)
            return True
        except (EOFError, TypeError, ValueError):
            self.logger.warning(f'Unable to save webpage to: {path}')
            return False

    @staticmethod
    def check_target_path(path: str, create=False, logger=None):
        """
        Check if a given path exists or not,
        if path not exists, program will be create them

        :param path: Target to check
        :param create: If is true, (path) will be created
        :param logger: Logger object for printing warnings and errors
        :returns : Returns true if (path) exists and if is created
        """

        if os.path.exists(path):
            return True
        elif create:
            prefix = ''
            if '/' == path[len(path) - 1]:
                path = path[:len(path) - 1]

            if '/' in path:
                if '/' == path[0]:
                    prefix = '/'
                    path = path[1:]

                paths = path.split('/')
                current_path = prefix
                for path in paths:
                    current_path += path + '/'
                    
                    try:
                        os.mkdir(current_path)
                    except PermissionError:
                        if logger is not None:
                            logger.error(f"No permission to create folder: {current_path}")
                            return False
                    except FileExistsError:
                        continue
            else:
                
                os.mkdir(path)
                return True
            return True
        else:
            return False
