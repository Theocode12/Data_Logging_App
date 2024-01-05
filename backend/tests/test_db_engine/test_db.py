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
        true_path = os.path.join(''.join([os.getcwd().split('backend')[0], "backend"]), f"data/{year}/{month:02d}/{day:02d}.txt")

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
        fd = self.db.open(path, 'x')
        self.assertEqual(fd, self.db.fd)
        self.assertIsInstance(fd, io.TextIOWrapper)
        self.db.close()

        # without path parameter
        fd = self.db.open(mode='r+')
        self.assertEqual(fd, self.db.fd)
        self.db.close()

        # raise exception when no path and no target is set
        with self.assertRaises(FileOpenError):
            self.db.target = None
            self.db.open()

    def test_close(self):
        path = os.path.join(self.tmpdir.name, "test.txt")
        self.db.open(path, 'x')
        self.db.close()
        self.assertIsNone(self.db.fd)

        # called when fd is none
        self.db.close()

    def test_write(self):
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        data = "hello world"
        with open(self.db.target, 'r+') as fd:
            self.db.fd = fd
            self.db.write(data)

        with open(self.db.target, 'r+') as fd:
            r_data = fd.readline()
        self.assertTrue(r_data, data)

    def test_readline(self):
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        data = "hello world"
        with open(self.db.target, 'w+') as fd:
            fd.write(data)

        with open(self.db.target, 'r+') as fd:
            self.db.fd = fd
            r_data = self.db.readline()

        self.assertEqual(data, r_data)

    def test_readlines(self):
        self.db.target = tempfile.mkstemp(dir=self.tmpdir.name, text=True)[1]
        data = ["hello world", "Data logging app"]
        with open(self.db.target, 'w+') as fd:
            for line in data:
                fd.write(line + "\n")

        with open(self.db.target, 'r+') as fd:
            self.db.fd = fd
            r_data = self.db.readlines()
            r_data = [line.rstrip("\n") for line in r_data]

        self.assertEqual(r_data, data)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()



class TestMetaDB(unittest.TestCase):
    def setUp(self):
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
        pass

    def test_retrieve_metadata(self):
        pass

    def test_save_metadata(self):
        pass





    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
