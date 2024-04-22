from typing import Dict, Optional
from models.exceptions.exception import GPSConnectionError, GPSDataError
from models.sensors.sensor import Sensor
from models import ModelLogger
from util import is_internet_connected
import gpsd
import requests


class OnlineGPS:
    class GPSResponse:
        def __init__(self, data):
            self.data = data

        def position(self):
            return self.data.get("longitude"), self.data.get("latitude")

        def speed(self):
            return None

        def altitude(self):
            return None

    def get_current(self):
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            if data["status"] == "success":
                latitude = data["lat"]
                longitude = data["lon"]
                return self.GPSResponse({"longitude": longitude, "latitude": latitude})
            else:
                print("Failed to retrieve location data:", data["message"])
        except Exception as e:
            print("An error occurred:", str(e))


class GPS(Sensor):
    """This class implements a way of consistently getting the relevant gps data in dictionary format"""

    def __init__(self, logger=None) -> None:
        """Constructor attempts to connect to the GPS device and sets up the data attribute to store date"""
        self.GPSResponse: Optional[gpsd.GpsResponse] = None
        self.data: Dict[str, Optional[float]] = {
            "longitude": None,
            "latitude": None,
            "altitude": None,
            "speed": None,
        }
        self.gps_logger = logger or ModelLogger("gps_tracker").customiseLogger()
        self.gps_logger.debug("GPSTracker Models logger started")

    def connect(self) -> None:
        """Attempts to connect to a GPS device"""
        try:
            gpsd.connect()

        except Exception:
            self.gps_logger.error("Could not connect to GPS device")
            raise GPSConnectionError("Could not connect to GPS device")

    def _pollGPSData(self, gps_obj: Optional[OnlineGPS] = None) -> None:
        """polls gps data from gps device and stores it in the data attribute"""
        try:
            if gps_obj is None:
                self.GPSResponse = gpsd.get_current()
            else:
                self.GPSResponse = gps_obj.get_current()
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
        set_methods = [
            method
            for method in dir(self)
            if callable(getattr(self, method)) and method.startswith("_set")
        ]
        for method_name in set_methods:
            getattr(self, method_name)()

    def get_data(self) -> Dict[str, Optional[float]]:
        try:
            self.connect()
        except GPSConnectionError:
            if is_internet_connected():
                oGPS = OnlineGPS()
                self._pollGPSData(oGPS)
        else:
            self._pollGPSData()
        return self.data


if __name__ == "__main__":
    gps = GPS()
    print(gps.get_data())
