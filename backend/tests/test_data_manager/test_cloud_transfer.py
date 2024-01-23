import unittest
from unittest.mock import MagicMock, patch
from models.data_manager.cloud_transfer import (
    CloudTransfer,
    mqtt,
    on_connection_closed,
    on_connection_failure,
    on_connection_interrupted,
    on_connection_resumed,
    on_connection_success,
)


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

    def test_load_from_env(self):
        pass

    # Add more tests as needed


if __name__ == "__main__":
    unittest.main()
