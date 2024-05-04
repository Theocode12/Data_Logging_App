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
            from models.db_engine.db import FileDB

            with FileDB(filename, "w") as db:
                db.write("")

        self.setFileHandler(filename)
        # self.setStreamHandler()

        if format:
            self.setFormatter(format)

        return self
