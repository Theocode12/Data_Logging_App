from models.db_engine.db import DBManager
from time import sleep

class DataCollectionManager:
    def __init__(self, cls, **kwargs):
        """kwarg are the locks and queues or probably manager"""
        self.db = DBManager(kwargs.get("lock"))
        self.data = {}
        self.data_models = []
        for c in cls:
            if callable(getattr(c, "get_data", None)):
                self.data_models.append(c)
            else:
                pass # Log the Issue

    def start(self):
        if self.data_models:
            while True:
                for model in self.data.models:
                    self.data.update(model.get_data())
                self.db.write(self.data)
                self.data.clear()
                sleep(1)

        else:
            pass # Log the Issue


# How do i stop the datacollection process. Idea is using events or some thing that can communicate between process



