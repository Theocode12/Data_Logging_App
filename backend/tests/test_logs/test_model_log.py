from models.sensors.gps import (
    GPS,
    GPSConnectionError,
    GPSDataError,
)
from models import ModelLogger
from unittest.mock import patch, Mock
from util.fake import Fake
from util.logger import BaseLogger
import unittest
import logging
import tracemalloc


class TestGPSLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tracemalloc.start()

    def setUp(self):

        ModelLogger.__bases__ = (Fake.imitate(BaseLogger, logging.Logger),)
        self.logger = ModelLogger("models.sensors.gps").customiseLogger()
        self.tracker = GPS(self.logger)

    def test_logging_level(self):
        self.logger.setLevel.assert_any_call(logging.DEBUG)

    def test_file_handler(self):
        self.logger.setFileHandler.assert_called()

    def test_console_handler(self):
        self.logger.setStreamHandler.assert_called()

    def test_set_log_format(self):
        self.logger.customiseLogger(
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        self.logger.setFormatter.assert_called()
        self.tracker.gps_logger.setFormatter.assert_called()

    def test_log_initialization_message(self):
        with patch("models.sensors.gps.ModelLogger", autospec=True) as mock_base_logger:
            GPS()
            mock_base_logger.return_value.debug.assert_called_once_with(
                "GPS Models logger started"
            )

    def test_logger_name(self):
        with patch("models.sensors.gps.ModelLogger") as mock_base_logger:
            tracker = GPS()
            mock_base_logger.assert_called_once_with("gps_tracker")

    def test_connection_error_logging(self):
        # Act & Assert
        with patch("gpsd.connect", side_effect=GPSConnectionError), patch(
            "models.sensors.gps.ModelLogger"
        ) as mock_base_logger:
            with self.assertRaises(GPSConnectionError):
                tracker = GPS()
                tracker.connect()
            mock_base_logger.error.assert_called_once_with(
                "Could not connect to GPS device"
            )

    def test_data_error_logging(self):
        with patch("gpsd.connect"), patch("gpsd.get_current", side_effect=GPSDataError):
            with patch("models.sensors.gps.ModelLogger") as mock_base_logger:
                with self.assertRaises(GPSDataError):
                    tracker = GPS()
                    tracker.connect()
                    tracker._pollGPSData()

        mock_base_logger.warning.assert_called_once_with(
            "Unexpected result from gps device"
        )


if __name__ == "__main__":
    unittest.main()
