from models.sensors.sensor import Sensor
import datetime


class Time(Sensor):

    def get_data(self):
        current_time = datetime.datetime.now()
        return {'time': current_time.strftime("%H:%M:%S")}

if __name__ == '__main__':
    time = Time()
    print(time.get_data())
