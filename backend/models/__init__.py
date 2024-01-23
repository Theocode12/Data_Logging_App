from utils.logger import BaseLogger
from utils import get_base_path
import logging
import os


class ModelLogger(BaseLogger):
    def __init__(self, name=None):
        super().__init__(name)

    def customiseLogger(
        self,
        level=logging.DEBUG,
        filename=os.path.join("{}".format(get_base_path()), "logs", "models.log"),
        format=None,
    ):
        self.setLevel(level)
        self.setFileHandler(filename)
        self.setStreamHandler()

        if format:
            self.setFormatter(format)

        return self
