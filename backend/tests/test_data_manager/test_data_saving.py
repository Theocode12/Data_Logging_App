from models.data_manager.data_saving import StorageManager, FileDB
from multiprocessing.connection import Pipe
from unittest.mock import MagicMock, patch
import logging
import unittest


logging.disable(logging.CRITICAL)


class TestDataSavingManager(unittest.TestCase):
    def setUp(self):
        self.mock_filedb = MagicMock(spec=FileDB)
        self.data_collection_manager = StorageManager()
        self.data_collection_manager.database = self.mock_filedb

    def test_set_database_path(self):
        with patch.object(
            FileDB, "create_file", return_value="/fake/db/path"
        ) as mock_filedb:
            data_saving_manager = StorageManager()
            self.assertEqual(data_saving_manager.db_path, "/fake/db/path")
            mock_filedb.create_file.return_value = "/fake/db/path"

    def test_save_collected_data(self):
        data = {"key": "value"}
        with patch("models.data_manager.data_saving.FileDB") as mock_db:
            data_saving_manager = StorageManager()
            data_saving_manager.save_collected_data(data)
            mock_db.return_value.__enter__.return_value.write_data_line.assert_called_once_with(
                data
            )

    def test_init_sensor_name(self):
        sensor_names = ["GPS"]
        with patch.object(FileDB, "create_file"):
            data_saving_manager = StorageManager(sensor_names)
            self.assertSequenceEqual(sensor_names, data_saving_manager.sensor_names)

    def test_get_required_data_with_one_sensorname(self):
        data = {"logitude": 89.32, "latitude": 171.22}
        with patch.object(FileDB, "create_file"):
            data_saving_manager = StorageManager(["logitude"])
            new_data = data_saving_manager.get_specified_data(data)
            self.assertDictEqual(new_data, {"logitude": 89.32})

    def test_get_required_data_with_multiple_sensornames(self):
        data = {"logitude": 89.32, "latitude": 171.22}
        with patch.object(FileDB, "create_file"):
            data_saving_manager = StorageManager(["logitude", "latitude"])
            new_data = data_saving_manager.get_specified_data(data)
            self.assertDictEqual(new_data, data)

    def test_get_required_data_with_wrong_sensor_name(self):
        data = {"logitude": 89.32, "latitude": 171.22}
        with patch.object(FileDB, "create_file"):
            data_saving_manager = StorageManager(["longitude"])
            with self.assertRaises(KeyError):
                data_saving_manager.get_specified_data(data)

    def test_get_required_data_with_no_sensor_name(self):
        data = {"logitude": 89.32, "latitude": 171.22}
        with patch.object(FileDB, "create_file"):
            data_saving_manager = StorageManager()
            new_data = data_saving_manager.get_specified_data(data)
            self.assertDictEqual(new_data, data)

    def test_run_method(self):
        test_data = {"sensor1": "value1", "sensor2": "value2"}

        comm_pipe, recv_comm_pipe = Pipe()
        send_data_pipe, recv_data_pipe = Pipe()

        with patch.object(
            StorageManager, "save_collected_data", autospec=True
        ) as mock_save_method:
            manager = StorageManager(sensor_names=["sensor1", "sensor2"])
            send_data_pipe.send(test_data)  # Simulate receiving data

            # Send stop command to exit the while loop
            comm_pipe.send("END")

            # Run the method
            manager.run(recv_comm_pipe, recv_data_pipe)

        # Assert that the save_collected_data method was called with the correct data
        mock_save_method.assert_called_once_with(
            manager, {"sensor1": "value1", "sensor2": "value2"}
        )


if __name__ == "__main__":
    unittest.main()
