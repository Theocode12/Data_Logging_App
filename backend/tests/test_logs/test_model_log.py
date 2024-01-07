from models.data_models.gps_tracker import (
    GPSTracker,
    GPSConnectionError,
    GPSDataError,
    gpsd,
    BaseModelLogger,
)
from unittest.mock import patch, Mock
from utils.fake import Fake
from utils.logger import BaseLogger
import unittest
import logging
import tracemalloc


class TestGPSTrackerLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tracemalloc.start()

    def setUp(self):

        BaseModelLogger.__bases__ = (Fake.imitate(BaseLogger, logging.Logger),)
        self.logger = BaseModelLogger("data_models.gps_tracker")
        self.tracker = GPSTracker(self.logger)

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
        with patch(
            "models.data_models.gps_tracker.BaseModelLogger", autospec=True
        ) as mock_base_logger:
            GPSTracker()
            mock_base_logger.return_value.debug.assert_called_once_with(
                "GPSTracker Models logger started"
            )

    def test_logger_name(self):
        with patch(
            "models.data_models.gps_tracker.BaseModelLogger", autospec=True
        ) as mock_base_logger:
            tracker = GPSTracker()
            mock_base_logger.assert_called_once_with("data_models.gps_tracker")
            self.assertEqual(tracker.gps_logger, mock_base_logger.return_value)

    def test_connection_error_logging(self):
        # Act & Assert
        with patch(
            "gpsd.connect", side_effect=GPSConnectionError, autospec=True
        ), patch(
            "models.data_models.gps_tracker.BaseModelLogger", autospec=True
        ) as mock_base_logger:
            with self.assertRaises(GPSConnectionError):
                tracker = GPSTracker()
                tracker.connect()
            mock_base_logger.error.assert_called_once_with(
                "Could not connect to GPS device"
            )

    def test_data_error_logging(self):
        with patch("gpsd.connect", autospec=True), patch(
            "gpsd.get_current", side_effect=GPSDataError, autospec=True
        ):
            with patch(
                "models.data_models.gps_tracker.BaseModelLogger", autospec=True
            ) as mock_base_logger:
                with self.assertRaises(GPSDataError):
                    tracker = GPSTracker()
                    tracker.connect()
                    tracker._pollGPSData()

        mock_base_logger.warning.assert_called_once_with(
            "Unexpected result from gps device"
        )


if __name__ == "__main__":
    unittest.main()
