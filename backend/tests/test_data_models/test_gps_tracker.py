from models.data_models import gps_tracker
from unittest.mock import patch, Mock
import unittest
import io
import tracemalloc


class TestGpsTracker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tracemalloc.start()

    def setUp(self):
        self.logging_patch = patch(
            "models.data_models.gps_tracker.ModelLogger", autospec=True
        )
        self.mock_logging = self.logging_patch.start()

        self.tracker = gps_tracker.GPSTracker()

        attrs = {
            "position.return_value": (-77.0364, 38.8951),
            "altitude.return_value": 30.433,
            "speed.return_value": 20.2,
        }
        self.GPSResponse = Mock(spec_set=gps_tracker.gpsd.GpsResponse, **attrs)

    def test_successful_gps_connection(self):
        """Simulate a successful connection to the GPS device"""
        with patch.object(
            gps_tracker.gpsd, "connect", return_value=None
        ) as mock_method:
            self.tracker.connect()
            mock_method.assert_called_once()

    def test_gps_connection_failure(self):
        """Simulate a failed connection to the GPS device"""
        with patch("sys.stderr", new_callable=io.StringIO), patch.object(
            gps_tracker.gpsd, "connect", side_effect=gps_tracker.GPSConnectionError
        ) as mock_method:
            with self.assertRaises(gps_tracker.GPSConnectionError):
                self.tracker.connect()
                mock_method.assert_called_once()

    def test_gathering_gps_data(self):
        """Simulata a successful gathering of required GPS data"""
        self.tracker.GPSResponse = self.GPSResponse
        self.tracker._gather_data()
        self.assertDictEqual(
            self.tracker.data,
            {
                "longitude": -77.0364,
                "latitude": 38.8951,
                "altitude": 30.433,
                "speed": 20.2,
            },
        )

    def test_gps_data_retrieval(self):
        """Test if GPS data is available"""
        with patch.object(
            gps_tracker.gpsd, "get_current", return_value=self.GPSResponse
        ) as mock_method:
            self.tracker._pollGPSData()
            mock_method.assert_called_once()

    def test_exception_handling_in_gps_data_retrieval(self):
        """Test for failure in gathering of GPS data"""
        with patch("sys.stderr", new_callable=io.StringIO), patch.object(
            gps_tracker.gpsd, "get_current", side_effect=gps_tracker.GPSDataError
        ) as mock_method:
            with self.assertRaises(gps_tracker.GPSDataError):
                self.tracker._pollGPSData()
                mock_method.assert_called_once()

    def test_gps_data_initialization(self):
        """Make sure GPS data to be collected is initialized correctly"""
        self.assertDictEqual(
            self.tracker.data,
            {"longitude": None, "latitude": None, "altitude": None, "speed": None},
        )

    def test_gps_connection_retry(self):
        with patch("sys.stderr", new_callable=io.StringIO), patch.object(
            gps_tracker.gpsd,
            "connect",
            side_effect=[gps_tracker.GPSConnectionError, None],
        ) as mock_method:
            with self.assertRaises(gps_tracker.GPSConnectionError):
                self.tracker.connect()
            self.tracker.connect()
            self.assertEqual(mock_method.call_count, 2)

    def test_gps_data_integrity(self):
        pass

    def tearDown(self) -> None:
        self.logging_patch.stop()

    @classmethod
    def tearDownClass(cls) -> None:
        tracemalloc.stop()


if __name__ == "__main__":
    unittest.main()
