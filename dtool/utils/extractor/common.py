from dtool.utils.extractor.platzi import PlatziExtractor


class ResourceExtractor:
    def __init__(self, logger, settings, page_source, url):
        self.logger = logger
        self.settings = settings
        self.page_source = page_source
        self.url = url

    def extract(self):
        extractor = False
        # validate URLs
        if PlatziExtractor.validate(self.url):
            if isinstance(self.page_source, str):
                extractor = PlatziExtractor(self.logger, self.page_source)
            else:
                self.logger.warning("Page content is not valid.")
                return {'result': False}
        else:
            self.logger.error(f"{self.url} is not a valid Platzi URL")

        # validate extractor value
        if not isinstance(extractor, bool):
            result = extractor.get_data()  # expected to be a dict or bool
            if result:
                return {'result': True, 'data': result}
            else:
                return {'result': False}
        else:
            return {'result': False}
