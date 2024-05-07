from models.sensors.sensor import Sensor
import datetime

class Date(Sensor):
    def get_data(self):
        current_date = datetime.datetime.now().date()
        return {'date': str(current_date)}


if __name__ == '__main__':
    date = Date()
    print(date.get_data())
