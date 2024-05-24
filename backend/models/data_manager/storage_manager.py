from multiprocessing.connection import Connection
from models.db_engine.db import FileDB
from models import ModelLogger
from typing import Sequence, Dict
from util import get_base_path
import os


class DSlogger:
    """
    Class for logging database activities.
    """

    logger = ModelLogger("data-saving").customiseLogger(
        filename=os.path.join("{}".format(get_base_path()), "logs", "storage.log")
    )


class StorageManager:
    """
    Manages data collection from specified data models and stores it in a file-based database.

    Attributes:
    - sensor_names (Sequence[str]): Names of sensors to store in the database.
    - db_path (str): Path to the file-based database.

    Methods:
    - __init__(self, sensor_names: Sequence[str] = [], **kwargs): Initialize the StorageManager instance with specified sensors and additional parameters.
    - get_data_from_specified_sensor(self, data: Dict[str, str]) -> Dict[str, str]: Filter and return data from the specified sensors.
    - save_collected_data(self, data: Dict) -> None: Save the collected data to the database.
    - run(self, recv_cmd_pipe: Connection, data_pipe: Connection) -> None: Main logic for data storage, which runs in a loop until a termination command is received.
    """

    def __init__(self, sensor_names: Sequence[str] = [], **kwargs):
        """
        Initialize the StorageManager instance.

        Parameters:
        - sensor_names (Sequence[str]): Names of sensors to store in the database.
        - kwargs: Additional parameters (locks, queues, or managers).
        """
        self.sensor_names = sensor_names
        self.db_path = FileDB().create_file()
        DSlogger.logger.info("Ready to saving to database")

    def get_data_from_specified_sensor(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Get data from the specified sensors.

        Parameters:
        - data (Dict[str, str]): Data from all available sensors.

        Returns:
        - Dict[str, str]: Filtered data containing only the specified sensors.
        """
        if not self.sensor_names:
            return data

        new_data = {}
        for sensor_name in self.sensor_names:
            new_data[sensor_name] = data[sensor_name]

        return new_data

    def save_collected_data(self, data: Dict) -> None:
        """
        Save the collected data to the database.

        Parameters:
        - data (Dict): Data to be saved.
        """
        with FileDB(self.db_path, "a") as db:
            db.write_data_line(data)

    def run(self, recv_cmd_pipe: Connection, data_pipe: Connection) -> None:
        """
        Main logic for data storage.

        Runs in a loop, polling data from sensors and saving it to the database until a termination command is received.

        Parameters:
        - recv_cmd_pipe (Connection): Pipe for receiving commands.
        - data_pipe (Connection): Pipe for receiving data.
        """
        while True:
            if data_pipe.poll():
                data = data_pipe.recv()
                DSlogger.logger.info(f"Data: {data} polled successfully")
                data = self.get_data_from_specified_sensor(data)
                self.save_collected_data(data)
                DSlogger.logger.info(f"Data: {data} saved successfully")
            if recv_cmd_pipe.poll():
                command = recv_cmd_pipe.recv()
                if command == "END":
                    DSlogger.logger.info(f"Stopped saving data to database")
                    break
