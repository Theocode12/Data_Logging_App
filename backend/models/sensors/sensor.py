class Sensor:
    """
    Base class for all sensor types.

    Methods:
    - get_data(): Abstract method to be implemented by subclasses to retrieve sensor data.
    """
    def get_data(self):
        raise NotImplementedError(
            f"get_data function for {self.__class__.__name__} is not implemented"
        )
