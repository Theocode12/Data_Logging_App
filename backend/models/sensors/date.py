from models.sensors.sensor import Sensor
import datetime

class Date(Sensor):
    """
    A sensor class that retrieves the current date.

    Inherits from the Sensor base class and implements the get_data method
    to return the current date.

    Methods:
    - get_data() -> dict: Retrieves the current date.
    """

    def get_data(self) -> dict:
        """
        Retrieves the current date.

        Returns:
        - dict: A dictionary with the current date in the format {"date": "YYYY-MM-DD"}.
        """
        current_date = datetime.datetime.now().date()
        return {"date": str(current_date)}


if __name__ == "__main__":
    date = Date()
    print(date.get_data())
