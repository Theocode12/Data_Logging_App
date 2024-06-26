from util.logger import BaseLogger
from util import get_base_path
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

        if not os.path.exists(filename):
            with open(filename, "w") as fd:
                fd.write("")

        self.setFileHandler(filename)
        # self.setStreamHandler()

        if format:
            self.setFormatter(format)

        return self
