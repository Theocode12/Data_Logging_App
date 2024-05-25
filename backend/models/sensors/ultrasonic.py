from typing import Dict, Optional
from models.sensors.sensor import Sensor
from models import ModelLogger
import RPi.GPIO as GPIO
import time


class Ultrasoniclogger:
    """
    Logger for the GPS module.

    Attributes:
    - logger: A customized logger instance for the GPS module, logging to gps.log.
    """
    logger = ModelLogger("ultrasonic").customiseLogger()


class Ultrasonic(Sensor):
    """Class to interact with an ultrasonic sensor to measure distance."""

    def __init__(self, trigger_pin: int = None, echo_pin: int = None, logger=None) -> None:
        """Initialize the ultrasonic sensor with specified trigger and echo pins."""
        try:
            self.trigger_pin = int(trigger_pin)
        except Exception:
            self.trigger_pin = 5
        try:
            self.echo_pin = int(echo_pin)
        except Exception:
            self.echo_pin = 6
        self.logger = logger
        self.data: Dict[str, Optional[float]] = {"distance": None}

        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def measure_distance(self) -> float:
        """Measures the distance using the ultrasonic sensor."""
        # Ensure the trigger pin is low
        GPIO.output(self.trigger_pin, GPIO.LOW)
        time.sleep(0.2)

        # Send a 10us pulse to trigger the sensor
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, GPIO.LOW)

        # Wait for the echo pin to go high and record the start time
        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()

        # Wait for the echo pin to go low and record the end time
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()

        # Calculate the duration of the pulse
        pulse_duration = pulse_end - pulse_start

        # Distance calculation (speed of sound is 34300 cm/s)
        distance = pulse_duration * 34300 / 2
        return round(distance, 2)

    def get_data(self) -> Dict[str, Optional[float]]:
        """Retrieve the distance data from the ultrasonic sensor."""
        try:
            self.data["distance"] = self.measure_distance()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to retrieve data: {e}")
            self.data["distance"] = None
        return self.data

    def cleanup(self):
        """Clean up GPIO settings."""
        GPIO.cleanup()

# Example usage:
if __name__ == "__main__":
    ultrasonic_sensor = Ultrasonic(trigger_pin=23, echo_pin=24)
    try:
        while True:
            distance = ultrasonic_sensor.get_data()
            print(f"Distance: {distance['distance']} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        ultrasonic_sensor.cleanup()
