class Sensor:
    def get_data(self):
        raise NotImplementedError(
            f" get_data function for {self.__class__.__name__} is not implemented"
        )
