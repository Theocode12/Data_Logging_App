from models.db_engine.db import FileDB, MetaDB
from models.data_models import *
from time import sleep
from typing import List, Optional


class DataCollectionManager:
    """
    Manages data collection from specified data models and stores it in a file-based database.
    """

    collection_interval: Optional[int] = None

    def __init__(self, data_model_names: Optional[List[str]] = None, **kwargs):
        """
        Initialize the DataCollectionManager instance.

        Args:
        - data_model_names (List[str]): Names of data models to use.
        - kwargs: Additional parameters (locks, queues, or managers).
        """
        self.database = FileDB()
        self.collected_data = {}
        self.data_models = set()

        self.set_database_path()

        if data_model_names:
            data_models = self.convert_data_model_names_to_classes(data_model_names)
            self.add_data_models(data_models)
        else:
            self.retrieve_all_data_models()

    def add_data_models(self, data_models: List[object]) -> None:
        """
        Add data models to the set of data models.

        Args:
        - data_models (List[object]): List of data models to add.
        """
        valid_data_models = [
            model for model in data_models if self.is_valid_data_model(model)
        ]
        self.data_models.update(valid_data_models)

    def clear_collected_data(self) -> None:
        """Clear the collected data."""
        self.collected_data.clear()

    def convert_data_model_names_to_classes(
        self, data_model_names: List[str]
    ) -> List[object]:
        """
        Convert data model names to data model classes.

        Args:
        - data_model_names (List[str]): Names of data models.

        Returns:
        - List[object]: List of data model classes.
        """
        data_models = [eval(model_name) for model_name in data_model_names]
        return data_models

    def is_valid_data_model(self, data_model: object) -> bool:
        """
        Check if the given object is a valid data model.

        Args:
        - data_model (object): The object to check.

        Returns:
        - bool: True if the object is a valid data model, False otherwise.
        """
        return callable(getattr(data_model, "get_data", None))

    def get_data_from_models(self) -> dict:
        """
        Get data from all registered data models.

        Returns:
        - dict: Collected data from data models.
        """
        for model in self.data_models:
            self.collected_data.update(model.get_data())
        return self.collected_data

    def retrieve_all_data_models(self) -> None:
        """Retrieve all available data models."""
        # Implementation for retrieving data models from wherever they are stored
        pass

    def set_database_path(self) -> None:
        """Set the file path for the database."""
        db_path = self.database.create_file()
        self.database.set_target(db_path)

    def save_collected_data(self) -> None:
        """Save the collected data to the database."""
        with self.database as db:
            db.write(self.collected_data)
        self.clear_collected_data()

    def run(self):
        pass
