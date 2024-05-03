from multiprocessing.connection import Connection
from models.db_engine.db import FileDB
from models import ModelLogger
from typing import Sequence, Dict


class DSlogger:
    logger = ModelLogger("data-saving").customiseLogger()

class DataSavingManager:
    """
    Manages data collection from specified data models and stores it in a file-based database.
    """

    def __init__(self, sensor_names: Sequence[str] = [], **kwargs):
        """
        Initialize the DataSavingManager instance.

        Args:
        - sensor_names (List[str]): Names of sensor to store in database.
        - kwargs: Additional parameters (locks, queues, or managers).
        """
        self.sensor_names = sensor_names
        self.db_path = FileDB().create_file()
        DSlogger.logger.info("Ready to saving to database")

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

    def run(
        self,
        recv_cmd_pipe: Connection,
        data_pipe: Connection,
    ) -> None:
        while True:
            if data_pipe.poll():
                data = data_pipe.recv()
                DSlogger.logger.info(f"Data: {data} polled successfully")
                data = self.get_specified_data(data)
                self.save_collected_data(data)
                DSlogger.logger.info(f"Data: {data} saved successfully")
            if recv_cmd_pipe.poll():
                command = recv_cmd_pipe.recv()
                if command == "END":
                    DSlogger.logger.info(f'Stopped saving data to database')
                    break
