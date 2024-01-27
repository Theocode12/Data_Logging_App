from unittest.mock import MagicMock, patch
from models.data_manager.cloud_transfer import (
    CloudTransfer,
    CloudTransferManager,
    mqtt,
    on_connection_closed,
    on_connection_failure,
    on_connection_interrupted,
    on_connection_resumed,
    on_connection_success,
)
from models.exceptions.exception import AWSCloudUploadError
from tempfile import mkstemp
import logging
import unittest

logging.disable(logging.CRITICAL)


class TestCloudTransfer(unittest.TestCase):
    def setUp(self):
        # Mock the MetaDB class to avoid actual file operations
        self.meta_db_mock = MagicMock()
        self.meta_db_patch = patch(
            "models.data_manager.cloud_transfer.MetaDB", self.meta_db_mock
        )
        self.meta_db_patch.start()

        # Mock the mqtt_connection_builder module
        self.mqtt_connection_builder_mock = MagicMock()
        self.mqtt_connection_builder_patch = patch(
            "models.data_manager.cloud_transfer.mqtt_connection_builder",
            self.mqtt_connection_builder_mock,
        )
        self.mqtt_connection_builder_patch.start()

        # Create an instance of CloudTransfer for testing
        self.cloud_transfer = CloudTransfer()

    def tearDown(self):
        # Stop the patches
        self.meta_db_patch.stop()
        self.mqtt_connection_builder_patch.stop()

    def test_connect(self):
        # Mock the mqtt_connection.connect method
        connect_mock = MagicMock()
        self.mqtt_connection_builder_mock.mtls_from_path.return_value.connect.return_value = (
            connect_mock
        )

        # Call the connect method and assert that mqtt_connection_builder.mtls_from_path is called with the correct arguments
        self.cloud_transfer.connect()
        self.mqtt_connection_builder_mock.mtls_from_path.assert_called_once_with(
            endpoint=self.cloud_transfer.endpoint,
            cert_filepath=self.cloud_transfer.cert_filepath,
            pri_key_filepath=self.cloud_transfer.pri_key_filepath,
            ca_filepath=self.cloud_transfer.ca_filepath,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=self.cloud_transfer.client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None,
            on_connection_success=on_connection_success,
            on_connection_failure=on_connection_failure,
            on_connection_closed=on_connection_closed,
        )

        # Assert that mqtt_connection.connect is called
        connect_mock.result.assert_called_once()

    def test_disconnect(self):
        disconnect_mock = MagicMock()
        self.mqtt_connection_builder_mock.mtls_from_path.return_value.disconnect.return_value = (
            disconnect_mock
        )

        self.cloud_transfer.connect()
        self.cloud_transfer.disconnect()
        disconnect_mock.result.assert_called_once()

    def test_publish(self):
        # Mock the mqtt_connection.publish method
        self.cloud_transfer.connect()
        publish_mock = MagicMock()
        self.cloud_transfer.mqtt_connection.publish = publish_mock

        # Call the publish method and assert that mqtt_connection.publish is called with the correct arguments
        data = {"key": "value"}
        self.cloud_transfer.publish(data)
        publish_mock.assert_called_once_with(
            topic=self.cloud_transfer.message_topic,
            payload='{"key": "value"}',
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    @patch(
        "models.data_manager.cloud_transfer.os.path.join", return_value="/fake/env/path"
    )
    @patch(
        "models.data_manager.cloud_transfer.dotenv_values",
        return_value={
            "endpoint": "fake_endpoint",
            "cert_filepath": "fake_cert_filepath",
        },
    )
    @patch(
        "models.data_manager.cloud_transfer.get_base_path",
        return_value="/fake/base/path",
    )
    def test_load_env(self, mock_get_base_path, mock_dotenv_values, mock_os_path_join):
        self.cloud_transfer._load_env()
        mock_get_base_path.assert_called_once()
        mock_os_path_join.assert_called_once_with("/fake/base/path", "config", ".env")
        mock_dotenv_values.assert_called_once_with("/fake/env/path")
        self.assertEqual(self.cloud_transfer.endpoint, "fake_endpoint")
        self.assertEqual(self.cloud_transfer.cert_filepath, "fake_cert_filepath")


class TestCloudTransferManager(unittest.TestCase):
    @patch(
        "models.data_manager.cloud_transfer.is_internet_connected", return_value=True
    )
    def test_init_with_internet_connection(self, mock_is_internet_connected):
        with patch(
            "models.data_manager.cloud_transfer.CloudTransfer"
        ) as MockCloudTransfer:
            manager = CloudTransferManager()

            self.assertTrue(mock_is_internet_connected.called)
            MockCloudTransfer.assert_called_once()
            MockCloudTransfer.return_value.connect.assert_called_once()
            self.assertIsNotNone(manager.cloud_transfer)

    @patch(
        "models.data_manager.cloud_transfer.is_internet_connected", return_value=False
    )
    def test_init_without_internet_connection(self, mock_is_internet_connected):
        with patch(
            "models.data_manager.cloud_transfer.CloudTransfer"
        ) as MockCloudTransfer:
            CloudTransferManager()

            self.assertTrue(mock_is_internet_connected.called)
            MockCloudTransfer.return_value.connect.assert_not_called()

    @patch(
        "models.data_manager.cloud_transfer.is_internet_connected", return_value=True
    )
    @patch(
        "models.data_manager.cloud_transfer.modify_data_to_dict",
        return_value={"key": "value"},
    )
    def test_upload_file(self, mock_modify_data_to_dict, mock_is_internet_connected):
        with patch.object(CloudTransfer, "connect"):
            manager = CloudTransferManager()
            manager._is_connected = MagicMock(return_value=True)
            manager.cloud_transfer.publish = MagicMock()
            manager.cloud_transfer.connect = MagicMock(return_value=True)
            manager.meta_db.set_target = MagicMock()
            manager.meta_db.readlines = MagicMock(return_value=["line1"])
            manager.meta_db.save_metadata = MagicMock()

            tmp_filepath = mkstemp()[1]
            manager.meta_db.target = tmp_filepath

            manager.upload_file("/fake/file/path.txt")

            # Assert
            mock_is_internet_connected.assert_called_once()
            manager._is_connected.assert_called_once()
            manager.meta_db.set_target.assert_called_once_with("/fake/file/path.txt")
            manager.meta_db.readlines.assert_called_once_with(0)
            mock_modify_data_to_dict.assert_called_once_with("line1")
            manager.cloud_transfer.publish.assert_called_once_with({"key": "value"})
            manager.meta_db.save_metadata.assert_called_once_with(
                meta={"LastUploadFile": "/fake/file/path.txt", "Offset": 0}
            )

    def test_is_connected(self):
        with patch.object(CloudTransfer, "connect"), patch(
            "models.data_manager.cloud_transfer.is_internet_connected",
            return_value=True,
        ):
            manager = CloudTransferManager()
            manager.cloud_transfer.connected = True

            result = manager._is_connected()
            self.assertTrue(result)

            manager.cloud_transfer.connected = False
            result = manager._is_connected()
            self.assertFalse(result)

    @patch.object(CloudTransferManager, "upload_file", side_effect=[Exception])
    def test_upload_file_connection_failure(self, mock_upload_file):
        with patch(
            "models.data_manager.cloud_transfer.is_internet_connected",
            return_value=False,
        ):
            manager = CloudTransferManager()

            with self.assertRaises(AWSCloudUploadError):
                manager.upload_files("/fake/file/", ["fake.txt"])

            mock_upload_file.assert_called_once_with("/fake/file/fake.txt")

    @patch(
        "models.data_manager.cloud_transfer.get_base_path",
        return_value="/fake/base/path",
    )
    @patch("models.data_manager.cloud_transfer.MetaDB")
    def test_batch_upload(
        self,
        mock_metadb,
        mock_get_base_path,
    ):
        with patch.object(CloudTransfer, "connect"), patch(
            "models.data_manager.cloud_transfer.is_internet_connected",
            return_value=True,
        ) as mock_is_internet_connected, patch.object(
            CloudTransferManager, "_is_connected", return_value=True
        ):
            manager = CloudTransferManager()
            manager.get_unuploaded_files = MagicMock(
                return_value=["file1.txt", "file2.txt"]
            )
            manager.upload_files = MagicMock()

            manager.batch_upload()

            mock_get_base_path.assert_called()
            mock_metadb.assert_called_once()
            self.assertTrue(mock_is_internet_connected.called)
            manager.get_unuploaded_files.assert_called()
            manager.upload_files.assert_called_once_with(
                "/fake/base/path/data/", ["file1.txt", "file2.txt"]
            )

    @patch(
        "models.data_manager.cloud_transfer.is_internet_connected", return_value=True
    )
    @patch(
        "models.data_manager.cloud_transfer.get_base_path",
        return_value="/fake/base/path",
    )
    @patch("models.data_manager.cloud_transfer.MetaDB")
    def test_batch_upload_no_internet_connection(
        self, mock_metadb, mock_get_base_path, mock_is_internet_connected
    ):
        with patch.object(CloudTransfer, "connect"):
            manager = CloudTransferManager()
            manager.get_unuploaded_files = MagicMock(
                return_value=["file1.txt", "file2.txt"]
            )
            manager.upload_files = MagicMock()

            with patch(
                "models.data_manager.cloud_transfer.is_internet_connected",
                return_value=False,
            ):
                manager.batch_upload()

            mock_get_base_path.assert_called()
            mock_metadb.assert_called_once()
            self.assertTrue(mock_is_internet_connected.called)
            manager.get_unuploaded_files.assert_not_called()
            manager.upload_files.assert_not_called()


if __name__ == "__main__":
    unittest.main()
