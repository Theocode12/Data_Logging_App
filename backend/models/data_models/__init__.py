from utils.logger import BaseLogger
import logging


class BaseModelLogger(BaseLogger):
    def __init__(self, name=None):
        super().__init__(name)

    def customiseLogger(self, level=logging.DEBUG, filename="./logs/models.log", format=None):
        self.setLevel(level)
        self.setFileHandler(filename)
        self.setStreamHandler()

        if format:
            self.setFormatter(format)

        return self

