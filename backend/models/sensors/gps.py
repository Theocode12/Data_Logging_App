from typing import Dict, Optional
from models.exceptions.exception import GPSConnectionError, GPSDataError
from models.sensors.sensor import Sensor
from models import ModelLogger
from util import is_internet_connected, get_base_path
import gpsd
import requests
import os


class GPSlogger:
    """
    Logger for the GPS module.

    Attributes:
    - logger: A customized logger instance for the GPS module, logging to gps.log.
    """
    logger = ModelLogger("gps").customiseLogger(
        filename=os.path.join(get_base_path(), "logs", "gps.log")
    )

class OnlineGPS:
    """
    Class to retrieve GPS data from an online service when a GPS device is not available.

    Methods:
    - get_current() -> GPSResponse: Retrieves current GPS data from an online service.
    """

    class GPSResponse:
        """
        Inner class representing the GPS data response.

        Methods:
        - position() -> tuple: Returns the longitude and latitude from the response.
        - speed() -> None: Placeholder method for speed data.
        - altitude() -> None: Placeholder method for altitude data.
        """

        def __init__(self, data):
            self.data = data

        def position(self):
            return self.data.get("longitude"), self.data.get("latitude")

        def speed(self):
            return None

        def altitude(self):
            return None

    def get_current(self):
        """
        Retrieves current GPS data from an online service.

        Returns:
        - GPSResponse: An instance of the GPSResponse class containing longitude and latitude.
        """
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            if data["status"] == "success":
                latitude = data["lat"]
                longitude = data["lon"]
                return self.GPSResponse({"longitude": longitude, "latitude": latitude})
            else:
                GPSlogger.logger.error("Failed to retrieve location data: %s", data["message"])
        except Exception as e:
            GPSlogger.logger.error("An error occurred while accessing the internet: %s", str(e))

class GPS(Sensor):
    """
    This class implements a way of consistently getting the relevant GPS data in dictionary format.

    Attributes:
    - GPSResponse: Optional[gpsd.GpsResponse] = None
    - data: Dict[str, Optional[float]]: Dictionary to store longitude, latitude, altitude, and speed.

    Methods:
    - connect() -> None: Attempts to connect to a GPS device.
    - _pollGPSData(gps_obj: Optional[OnlineGPS] = None) -> None: Polls GPS data from the GPS device.
    - _set_pos() -> None: Stores the position (longitude and latitude) in the data attribute.
    - _set_alt() -> None: Stores the altitude in the data attribute.
    - _set_speed() -> None: Stores the speed in the data attribute.
    - _gather_data() -> None: Calls the relevant methods to store the data in the data attribute.
    - get_data() -> Dict[str, Optional[float]]: Retrieves GPS data and handles fallback to online GPS.
    """

    def __init__(self, logger=None) -> None:
        """
        Constructor attempts to connect to the GPS device and sets up the data attribute to store data.
        """
        self.GPSResponse: Optional[gpsd.GpsResponse] = None
        self.data: Dict[str, Optional[float]] = {
            "longitude": None,
            "latitude": None,
            "altitude": None,
            "speed": None,
        }

    def connect(self) -> None:
        """
        Attempts to connect to a GPS device.
        """
        try:
            gpsd.connect()
            GPSlogger.logger.info("Connecting to GPS hardware")
        except Exception:
            GPSlogger.logger.error("Could not connect to GPS device")
            raise GPSConnectionError("Could not connect to GPS device")

    def _pollGPSData(self, gps_obj: Optional[OnlineGPS] = None) -> None:
        """
        Polls GPS data from the GPS device and stores it in the data attribute.

        Parameters:
        - gps_obj (Optional[OnlineGPS]): An optional OnlineGPS object for fallback data retrieval.
        """
        try:
            if gps_obj is None:
                self.GPSResponse = gpsd.get_current()
            else:
                self.GPSResponse = gps_obj.get_current()
        except Exception:
            GPSlogger.logger.warning("GPS device not active")
            raise GPSDataError("GPS device not active")
        self._gather_data()

    def _set_pos(self) -> None:
        """
        Stores the position (longitude and latitude) from the GPS response in the data attribute.
        """
        try:
            self.data["longitude"], self.data["latitude"] = self.GPSResponse.position()
        except gpsd.NoFixError:
            pass

    def _set_alt(self) -> None:
        """
        Stores the altitude from the GPS response in the data attribute.
        """
        try:
            self.data["altitude"] = self.GPSResponse.altitude()
        except gpsd.NoFixError:
            pass

    def _set_speed(self) -> None:
        """
        Stores the speed from the GPS response in the data attribute.
        """
        try:
            self.data["speed"] = self.GPSResponse.speed()
        except gpsd.NoFixError:
            pass

    def _gather_data(self) -> None:
        """
        Calls the relevant methods to store the data in the data attribute.
        """
        set_methods = [
            method
            for method in dir(self)
            if callable(getattr(self, method)) and method.startswith("_set")
        ]
        for method_name in set_methods:
            getattr(self, method_name)()

    def get_data(self) -> Dict[str, Optional[float]]:
        """
        Retrieves GPS data and handles fallback to online GPS if necessary.

        Returns:
        - Dict[str, Optional[float]]: A dictionary containing GPS data (longitude, latitude, altitude, speed).
        """
        try:
            self.connect()
            self._pollGPSData()
        except (GPSConnectionError, GPSDataError):
            if is_internet_connected():
                GPSlogger.logger.info("Using Online GPS Feature")
                oGPS = OnlineGPS()
                self._pollGPSData(oGPS)
            else:
                GPSlogger.logger.info("Unable to use online GPS feature")

        return self.data

if __name__ == "__main__":
    gps = GPS()
    print(gps.get_data())
