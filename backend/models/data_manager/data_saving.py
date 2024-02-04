from multiprocessing.connection import Connection
from models.db_engine.db import FileDB
from typing import List, Dict


class DataSavingManager:
    """
    Manages data collection from specified data models and stores it in a file-based database.
    """

    def __init__(self, sensor_names: List[str] = [], **kwargs):
        """
        Initialize the DataSavingManager instance.

        Args:
        - sensor_names (List[str]): Names of sensor to store in database.
        - kwargs: Additional parameters (locks, queues, or managers).
        """
        self.sensor_names = sensor_names
        self.db_path = FileDB().create_file()

    def get_specified_data(self, data: Dict[str, str]):
        if not self.sensor_names:
            return data

        new_data = {}
        for sensor_name in self.sensor_names:
            new_data[sensor_name] = data[sensor_name]

        return new_data

    def save_collected_data(self, data: Dict) -> None:
        """Save the collected data to the database."""
        with FileDB(self.db_path, "a") as db:
            db.write_data_line(data)

    def run(self, recv_cmd_pipe: Connection, data_pipe: Connection) -> None:
        while True:
            if recv_cmd_pipe.poll():
                command = recv_cmd_pipe.recv()
                if command == "STOP":
                    break
            if data_pipe.poll():
                data = data_pipe.recv()
                self.save_collected_data(self.get_specified_data(data))
