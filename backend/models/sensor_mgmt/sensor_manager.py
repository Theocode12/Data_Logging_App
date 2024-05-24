from typing import Optional, List
from time import sleep
from multiprocessing.connection import Connection
from models.db_engine.db import TempDB
from models.sensor_mgmt.register_sensor import SensorModule
from models import ModelLogger
import importlib
import asyncio


class SensorManagerlogger:
    """
    A logger class for SensorManager that customizes the ModelLogger.
    """

    logger = ModelLogger("sensor-manager").customiseLogger()


class SensorDataManager:
    """
    Manages sensor data collection and temporary storage.

    Attributes:
    - COLLECTION_INTERVAL (Optional[int]): The interval for data collection in seconds.
    - data (dict): A dictionary to store sensor data.
    - tmp_db (TempDB): An instance of TempDB for temporary data storage.
    - sensors (list): A list of sensor instances.
    """

    COLLECTION_INTERVAL: Optional[int] = 10

    def __init__(self):
        """
        Initializes the SensorDataManager with sensor instances and an empty data dictionary.
        """
        self.data = {}
        self.tmp_db = TempDB()
        self.sensors = self.get_sensor_instances()

    def get_sensor_instances(self) -> List:
        """
        Retrieves instances of sensor classes.

        Returns:
        - List: A list of sensor instances.
        """
        sensor_instances = []
        try:
            getattr(self, "sensors")
        except AttributeError:
            sensor_modules = self.get_sensor_modules()
            sensor_classes = self.extract_sensor_classes(sensor_modules)
            for cls in sensor_classes:
                sensor_instances.append(cls())
        return sensor_instances

    def clear_data(self) -> None:
        """
        Clears the collected sensor data.
        """
        self.data = {}

    def get_data_from_sensors(self) -> dict:
        """
        Collects data from all sensor instances and updates the data attribute.

        Returns:
        - dict: The collected sensor data.

        Raises:
        - NotImplementedError: If a sensor's get_data method is not implemented.
        """
        self.clear_data()
        try:
            for sensor in self.sensors:
                self.data.update(sensor.get_data())
        except NotImplementedError as e:
            raise e
        return self.data

    def extract_sensor_classes(self, sensor_modules: List[str]) -> List:
        """
        Extracts sensor classes from module names.

        Args:
        - sensor_modules (List[str]): A list of sensor module names.

        Returns:
        - List: A list of sensor classes.
        """
        sensor_classes = []
        for sensor_module in sensor_modules:
            try:
                module_name, class_name = sensor_module.rsplit(".", 1)
                module = importlib.import_module(module_name)
                sensor_class = getattr(module, class_name)
                sensor_classes.append(sensor_class)
            except Exception as e:
                # Handle import errors or attribute errors
                SensorManagerlogger.logger.error("Error importing sensor modules")
        return sensor_classes

    def get_sensor_modules(self) -> List[str]:
        """
        Retrieves the list of sensor modules.

        Returns:
        - List[str]: A list of sensor module strings.
        """
        return SensorModule.MODULES

    def run(self, comm_pipe: Connection, data_pipe: Connection) -> None:
        """
        Continuously collects data from sensors and manages temporary storage
        based on commands received through a communication pipe.

        Args:
        - comm_pipe (Connection): The communication pipe for receiving commands.
        - data_pipe (Connection): The data pipe for sending collected data.

        Commands:
        - "END": Stops data collection and exits the loop.
        - "START": Initiates data storage.
        - "STOP": Stops data storage.
        """
        send_data = False
        db_lines = self.tmp_db.get_current_no_of_lines()
        while True:
            if comm_pipe.poll():
                command = comm_pipe.recv()
                if command == "END":
                    SensorManagerlogger.logger.info(
                        "Data Collection From Sensor Stopped"
                    )
                    exit()
                elif command == "START":
                    SensorManagerlogger.logger.info("Data storage initiated")
                    send_data = True
                elif command == "STOP":
                    SensorManagerlogger.logger.info("Data storage stopped")
                    send_data = False

            self.get_data_from_sensors()
            self.tmp_db.save_to_tmp_db(self.data)
            if send_data:
                data_pipe.send(self.data)
            if db_lines >= TempDB.MAX_DB_LINES:
                self.tmp_db.clean_up_tmp_db()
                db_lines = 0

            db_lines += 1
            sleep(20)
