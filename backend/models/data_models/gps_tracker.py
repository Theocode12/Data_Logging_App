from typing import Dict, Optional
from models.data_models import BaseModelLogger
import gpsd


class GPSTracker:
    """This class implements a way of consistently getting the relevant gps data in dictionary format"""
    def __init__(self, logger=None) -> None:
        """Constructor attempts to connect to the GPS device and sets up the data attribute to store date"""
        self.GPSResponse: Optional[gpsd.GpsResponse] = None
        self.data: Dict[str, Optional[float]] = {
            "longitude": None,
            "latitude": None,
            "altitude": None,
            "speed": None
            }
        self.gps_logger = logger or BaseModelLogger("data_models.gps_tracker")
        self.gps_logger.customiseLogger()
        self.gps_logger.debug("GPSTracker Models logger started")

    def connect(self) -> None:
        """Attempts to connect to a GPS device"""
        try:
            gpsd.connect()

        except Exception:
            self.gps_logger.error("Could not connect to GPS device")
            raise GPSConnectionError("Could not connect to GPS device")


    def _pollGPSData(self) -> None:
        """polls gps data from gps device and stores it in the data attribute"""
        try:
            self.GPSResponse = gpsd.get_current()
        except Exception:
            self.gps_logger.warning("Unexpected result from gps device")
            raise GPSDataError("Unexpected result from gps device")
        self._gather_data()

    def _set_pos(self) -> None:
        """Stores the position(longitude and lagtitude) from the gps response in the data attribute"""
        self.data["longitude"], self.data["latitude"] = self.GPSResponse.position()

    def _set_alt(self) -> None:
        """Stores the altitude from the gps response in the data attribute"""
        self.data["altitude"] = self.GPSResponse.altitude()

    def _set_speed(self) -> None:
        """Stores the speed from the gps response in the data attribute"""
        self.data["speed"] = self.GPSResponse.speed()

    def _gather_data(self) -> None:
        """Calls the relevant method to store the data in the data attribute"""
        set_methods = [method for method in dir(self) if callable(getattr(self, method)) and method.startswith('_set')]
        for method_name in set_methods:
            getattr(self, method_name)()

    def get_data(self) -> Dict[str, Optional[float]]:
        self._pollGPSData()
        return self.data


class GPSConnectionError(Exception):
    pass

class GPSDataError(Exception):
    pass
