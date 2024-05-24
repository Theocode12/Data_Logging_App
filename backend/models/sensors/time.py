from models.sensors.sensor import Sensor
import datetime


class Time(Sensor):
    """
    A sensor class that retrieves the current time.

    Inherits from the Sensor base class and implements the get_data method
    to return the current time.

    Methods:
    - get_data() -> dict: Retrieves the current time.
    """

    def get_data(self) -> dict:
        """
        Retrieves the current time.

        Returns:
        - dict: A dictionary with the current time in the format {"time": "HH:MM:SS"}.
        """
        current_time = datetime.datetime.now()
        return {"time": current_time.strftime("%H:%M:%S")}

if __name__ == "__main__":
    time = Time()
    print(time.get_data())
