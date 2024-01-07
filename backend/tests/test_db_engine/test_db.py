from models.db_engine.db import FileDB, MetaDB
from models.exceptions.exception import FileCloseError, FileOpenError
from datetime import datetime
import io
import unittest
import tempfile
import os
import shutil


class TestFileDB(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db = FileDB()

    def test_create_and_remove_dir(self):
        tmpdir = os.path.abspath("./tmp")
        self.db.create_dir(tmpdir)
        self.assertTrue(os.path.exists(tmpdir))
        self.db.remove_dir(tmpdir)
        self.assertFalse(os.path.exists(tmpdir))

    def test_create_and_delete_file_given_path(self):
        path = os.path.join(self.tmpdir.name, "test.txt")
        self.db.create_file(path)
        self.assertTrue(os.path.exists(path))
        self.db.delete_file(path)
        self.assertFalse(os.path.exists(path))

    def test_create_file_without_path(self):
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        true_path = os.path.join(
            "".join([os.getcwd().split("backend")[0], "backend"]),
            f"data/{year}/{month:02d}/{day:02d}.txt",
        )

        self.skipTest("Not Needed until application is running")
        if not os.path.exists(true_path):
            path = self.db.create_file()
            self.assertTrue(os.path.exists(path))
            self.assertEqual(path, true_path)
            os.remove(path)

    def test_set_target(self):
        # Test set_target without path parameter
        target = self.db.set_target()
        self.assertEqual(target, self.db.target)

        # Test set_target with path parameter
        path = "/tmp/test"
        self.db.set_target(path)
        self.assertEqual(path, self.db.target)

    def test_open(self):
        # With path parameter set
        path = os.path.join(self.tmpdir.name, "test.txt")
        fd = self.db.open(path, "x")
        self.assertEqual(fd, self.db.fd)
        self.assertIsInstance(fd, io.TextIOWrapper)
        self.db.close()

        # without path parameter
        fd = self.db.open(mode="r+")
        self.assertEqual(fd, self.db.fd)
        self.db.close()

        # raise exception when no path and no target is set
        with self.assertRaises(FileOpenError):
            self.db.target = None
            self.db.open()

    def test_close(self):
        path = os.path.join(self.tmpdir.name, "test.txt")
        self.db.open(path, "x")
        self.db.close()
        self.assertIsNone(self.db.fd)

        # called when fd is none
        self.db.close()

    def test_write(self):
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        data = "hello world"
        with open(self.db.target, "r+") as fd:
            self.db.fd = fd
            self.db.write(data)

        with open(self.db.target, "r+") as fd:
            r_data = fd.readline()
        self.assertTrue(r_data, data)

    def test_readline(self):
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        data = "hello world"
        with open(self.db.target, "w+") as fd:
            fd.write(data)

        with open(self.db.target, "r+") as fd:
            self.db.fd = fd
            r_data = self.db.readline()

        self.assertEqual(data, r_data)

    def test_readlines(self):
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        data = ["hello world", "Data logging app"]
        with open(self.db.target, "w+") as fd:
            for line in data:
                fd.write(line + "\n")

        with open(self.db.target, "r+") as fd:
            self.db.fd = fd
            r_data = self.db.readlines()
            r_data = [line.rstrip("\n") for line in r_data]

        self.assertEqual(r_data, data)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()


class TestMetaDB(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db = MetaDB()

    def test_clear_metadata(self):
        self.assertIsInstance(self.db.meta, dict)
        self.assertEqual(self.db.meta, {})

        self.db.meta = {"offset": 0, "target": "/tmp/test"}
        self.db.clear_metadata()
        self.assertDictEqual(self.db.meta, {})

    def test_update_metadata(self):
        meta = {"offset": 0, "target": "/tmp/test"}

        # Test when self.db.meta is empty
        self.db.update_metadata(meta)
        self.assertDictEqual(self.db.meta, meta)

        # Test when self.db.meta is not empty
        newmeta = {"offset": 1, "type": "backend"}
        self.db.update_metadata(newmeta)
        meta.update(newmeta)
        self.assertDictEqual(self.db.meta, meta)

    def test_get_metadata_path(self):
        # Test without custom_path parameter
        metadata_path = self.db._get_metadata_path()
        true_path = os.path.join(
            os.path.join(
                "".join([os.getcwd().split("backend")[0], "backend"]), "config"
            ),
            "meta.txt",
        )
        self.assertEqual(metadata_path, true_path)

        # Test with custom_path parameter
        metadata_path = self.db._get_metadata_path("test")
        true_path = os.path.join(
            os.path.join(
                "".join([os.getcwd().split("backend")[0], "backend"]), "config"
            ),
            "test",
        )
        self.assertEqual(metadata_path, true_path)

    def test_retrieve_metadata_lines(self):
        # create temporary directory and file
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]

        # Test when file is empty
        lines = self.db.retrieve_metadata_lines(self.db.target)
        self.assertEqual(len(lines), 0)

        # write to the file
        w_lines = ["file=/tmp/test", "offset=0"]
        with open(self.db.target, "w") as fd:
            for line in w_lines:
                fd.write(line + "\n")

        # Test when file is not empty
        lines = self.db.retrieve_metadata_lines(self.db.target)
        self.assertEqual(lines, w_lines)
        self.assertEqual(w_lines, self.db.metadata_lines)

    def test_updata_metadata_lines(self):
        # Test when metalines is empty
        lines = self.db.update_metadata_lines()
        self.assertEqual(len(lines), 0)
        # Test when Meta is provided
        self.db.metadata_lines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=0",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]
        newmeta = {"offset": 20}
        metadatalines = self.db.update_metadata_lines(newmeta)
        true_metadatalines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=20",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]
        self.assertEqual(metadatalines, true_metadatalines)

        # Test when meta is not provided but self.meta is present
        self.db.meta = {"offset": 0}
        true_metadatalines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=0",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]
        metadatalines = self.db.update_metadata_lines()
        self.assertEqual(true_metadatalines, metadatalines)

    def test_retrieve_metadata(self):
        metadata_lines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=0",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]

        # create temporary directory and file
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]

        with open(self.db.target, "w") as fd:
            for line in metadata_lines:
                fd.write(line + "\n")

        # Retrive metadata without args
        meta = self.db.retrieve_metadata(self.db.target)
        true_meta = {
            "offset": 0,
            "file": "/tmp/test",
            "GPS": "GPSTracker",
            "Battery": "Ba3Performance",
        }
        self.assertDictEqual(meta, true_meta)

        # Retrieve metadata with args
        self.db.clear_metadata()
        meta = self.db.retrieve_metadata(self.db.target, ["offset", "GPS", "Compass"])
        true_meta = {"offset": 0, "GPS": "GPSTracker"}
        self.assertDictEqual(meta, true_meta)

    def test_save_metadata(self):
        metadata_lines = metadata_lines = ["file=/tmp/test"]

        # create temporary directory and file
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]

        # save in an empty file
        self.db.save_metadata(self.db.target, {"file": "/tmp/test"})

        with open(self.db.target, "r") as fd:
            saved_metadatalines = fd.readlines()
            saved_metadatalines = [line.rstrip("\n") for line in saved_metadatalines]
        self.assertListEqual(saved_metadatalines, metadata_lines)

        # save in a non empty file
        metadata_lines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=0",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]

        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        with open(self.db.target, "w") as fd:
            for line in metadata_lines:
                fd.write(line + "\n")

        self.db.save_metadata(self.db.target, {"offset": 20})

        with open(self.db.target, "r") as fd:
            saved_metadatalines = fd.readlines()
            saved_metadatalines = [line.rstrip("\n") for line in saved_metadatalines]

        self.assertNotEqual(saved_metadatalines, metadata_lines)
        new_metadatalines = metadata_lines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=20",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]

        self.assertListEqual(saved_metadatalines, new_metadatalines)

    def test_readline(self):
        metadata_lines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=0",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]

        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        with open(self.db.target, "w") as fd:
            for line in metadata_lines:
                fd.write(line + "\n")

        # Test if offset value changes for first read
        meta = self.db.retrieve_metadata(self.db.target).copy()
        self.db.open(self.db.target, "r")
        line = self.db.readline()
        self.db.close()

        self.assertIsInstance(line, str)
        self.assertNotEqual(int(meta.get("offset")), int(self.db.meta.get("offset")))

        # Test if offset value updates for second read operation
        meta = self.db.meta.copy()
        self.db.open(self.db.target, "r")
        line = self.db.readline()
        self.db.close()

        self.assertIsInstance(line, str)
        self.assertNotEqual(int(meta.get("offset")), int(self.db.meta.get("offset")))

    def test_readlines(self):
        metadata_lines = [
            "# CloudTF metadata",
            "file=/tmp/test",
            "offset=0",
            "",
            "",
            "# Models Metadata",
            "GPS = GPSTracker",
            "Battery= Ba3Performance",
        ]

        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        with open(self.db.target, "w") as fd:
            for line in metadata_lines:
                fd.write(line + "\n")

        meta = self.db.retrieve_metadata(self.db.target).copy()
        self.db.open(self.db.target, "r")
        line = self.db.readlines()
        self.db.close()

        self.assertIsInstance(line, list)
        self.assertNotEqual(int(meta.get("offset")), int(self.db.meta.get("offset")))

    def test_full_functionality(self):
        # Mock data
        data = [
            {
                "longitude": -74.0364,
                "latitude": 36.8951,
                "altitude": 30.433,
                "speed": 20.0,
            },
            {
                "longitude": -77.0364,
                "latitude": 35.8951,
                "altitude": 30.433,
                "speed": 20.6,
            },
            {
                "longitude": -78.0364,
                "latitude": 34.8951,
                "altitude": 30.433,
                "speed": 24.2,
            },
            {
                "longitude": -77.0364,
                "latitude": 33.6541,
                "altitude": 32.433,
                "speed": 21.2,
            },
        ]

        # data file and its corresponding metafile
        datafile = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        metafile = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]

        # save data in datafile. This represents our database
        with open(datafile, "w") as file:
            for datum in data:
                line = ",".join([f"{key}={value}" for key, value in datum.items()])
                file.write(line + "\n")

        metadata = self.db.retrieve_metadata(metafile).copy()
        # Assert that the metadata is empty
        self.assertDictEqual(metadata, {})

        self.db.open(datafile, "r")
        line = self.db.readline()
        self.db.close()

        # Assert that line is a string
        self.assertIsInstance(line, str)

        newmeta_1 = self.db.meta.copy()
        # Assert metadata changes
        self.assertNotEqual(metadata, newmeta_1)

        self.db.save_metadata(metafile)

        retrived_metadata = self.db.retrieve_metadata(metafile).copy()

        # Assert Metadata is same after saving and retrival
        self.assertEqual(retrived_metadata, newmeta_1)

        # Read another line
        self.db.open(datafile, "r")
        line = self.db.readline()
        self.db.close()

        newmeta_2 = self.db.meta
        self.assertNotEqual(retrived_metadata, newmeta_2)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()


if __name__ == "__main__":
    unittest.main()
