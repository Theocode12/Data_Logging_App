import logging


class BaseLogger(logging.Logger):
    def __init__(self, name: str) -> None:
        self.logger: logging.Logger = logging.getLogger(name)
        self.format: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    def setLevel(self, level: int) -> None:
        return super().setLevel(level)

    def setFormatter(self, format: str) -> None:
        self.format = logging.Formatter(format)

    def getFormatter(self) -> logging.Formatter:
        return self.format

    def setFileHandler(self, filename: str) -> None:
        self.logger.addHandler(
            logging.FileHandler(filename).setFormatter(self.getFormatter())
        )

    def setStreamHandler(self) -> None:
        self.logger.addHandler(
            logging.StreamHandler().setFormatter(self.getFormatter())
        )
