from typing import Optional, List
from time import sleep
from multiprocessing.connection import Connection
from models.db_engine.db import TempDB
from models.sensor_mgmt.register_sensor import SensorModule
from models import ModelLogger
import importlib


class SensorManagerlogger:
    logger = ModelLogger("sensor-manager").customiseLogger()


class SensorDataManager:
    COLLECTION_INTERVAL: Optional[int] = 5

    def __init__(self):
        self.data = {}
        self.tmp_db = TempDB()
        self.sensors = self.get_sensor_instances()

    def get_sensor_instances(self):
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
        self.data = {}

    def get_data_from_sensors(self):
        self.clear_data()
        try:
            for sensor in self.sensors:
                self.data.update(sensor.get_data())
        except NotImplementedError as e:
            raise e

        return self.data

    def extract_sensor_classes(self, sensor_modules: List[str]):
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

    def get_sensor_modules(self):
        return SensorModule.MODULES

    def run(self, comm_pipe: Connection, data_pipe: Connection):
        send_data = False
        db_lines = self.tmp_db.get_current_db_lines()
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
                elif (
                    command == "STOP"
                ):  # Bug: Fix data-saving manager to send stop command
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
            sleep(self.COLLECTION_INTERVAL)
