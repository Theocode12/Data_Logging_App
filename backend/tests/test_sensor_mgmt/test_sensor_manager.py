# def setUp(self):
#         with patch.object(DataSavingManager, "set_database_path"):
#             self.mock_filedb = MagicMock(spec=FileDB)
#             self.data_collection_manager = DataSavingManager()
#             self.data_collection_manager.database = self.mock_filedb

#     def test_clear_collected_data(self):
#         # Test clearing collected data
#         self.data_collection_manager.collected_data = {"key": "value"}
#         self.data_collection_manager.clear_collected_data()
#         self.assertEqual(self.data_collection_manager.collected_data, {})

#     def test_convert_data_model_names_to_classes(self):
#         # Test converting data model names to classes
#         data_model_names = ["ModelA", "ModelB"]
#         with patch("builtins.eval", side_effect=[MagicMock(), MagicMock()]):
#             result = self.data_collection_manager.convert_data_model_names_to_classes(
#                 data_model_names
#             )
#         self.assertEqual(len(result), 2)

#     def test_is_valid_data_model(self):
#         # Test checking if an object is a valid data model
#         mock_data_model = MagicMock(spec=["get_data"])
#         self.assertTrue(
#             self.data_collection_manager.is_valid_data_model(mock_data_model)
#         )

#         invalid_data_model = MagicMock(spec=["gt_data"])
#         self.assertFalse(
#             self.data_collection_manager.is_valid_data_model(invalid_data_model)
#         )

#     def test_get_data_from_one_model(self):
#         # Test getting data from data models
#         mock_data_model = MagicMock(spec=["get_data"])
#         mock_data_model.get_data.return_value = {"key": "value"}
#         self.data_collection_manager.data_models = {mock_data_model}

#         result = self.data_collection_manager.get_data_from_models()
#         self.assertDictEqual(result, {"key": "value"})

#     def test_get_data_from_multiple_models(self):
#         mock_data_model_1 = MagicMock(spec=["get_data"])
#         mock_data_model_2 = MagicMock(spec=["get_data"])
#         mock_data_model_1.get_data.return_value = {"key_1": "value_1"}
#         mock_data_model_2.get_data.return_value = {"key_2": "value_2"}
#         self.data_collection_manager.data_models = {
#             mock_data_model_1,
#             mock_data_model_2,
#         }

#         result = self.data_collection_manager.get_data_from_models()
#         self.assertDictEqual(result, {"key_1": "value_1", "key_2": "value_2"})

#     def test_set_database_path(self):
#         self.mock_filedb.create_file.return_value = "/fake/db/path"
#         self.data_collection_manager.set_database_path()

#         self.assertEqual(
#             self.data_collection_manager.database.set_target.call_args[0][0],
#             "/fake/db/path",
#         )

#     def test_save_collected_data(self):
#         # Test saving collected data to the database
#         self.data_collection_manager.collected_data = {"key": "value"}
#         self.data_collection_manager.save_collected_data()

#         # Ensure that the correct method is called and collected data is cleared
#         self.mock_filedb.write_data_line.assert_called_once_with({"key": "value"})
#         self.assertEqual(self.data_collection_manager.collected_data, {})
