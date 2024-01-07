from models.exceptions.exception import (
    FileOpenError,
    FileReadError,
    FileWriteError,
    FileCloseError,
    CreateDirectoryError,
    RemoveDirectoryError,
)
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
import os
import io


class DBManager:
    meta = ""

    def __init__(self, lock=None):
        self.lock = lock
        self.db = FileDB()
        self.target = None

    def write(self, data):
        if not self.target:
            self._set_tagert()
        # Aquire the lock
        with open(self.target, mode="r+") as fd:
            fd.write(data)
        # Release the lock

    def read(self, *meta):
        pass

    def open(self, filename, mode):
        self.db.open(filename, mode)

    def close(self):
        self.db.close()

    def _set_tagert(self):
        self.target = self.db.init_file()


# New Idea: So i'm thinking of a way of writing or reading to file using an Open api from the which returns a file
# file descriptor for the file and we can read or write data to it. I want DB manager to handle this
# functionality.


class FileDB:

    """
    The DB class represents a simple file-based database manager.

    It provides methods for opening, closing, reading, and writing to files, as well as managing metadata.
    """

    def __init__(self) -> None:
        """
        Initialize the DB instance.

        Attributes:
        - target: The target file path.
        - fd: The file descriptor for the open file.
        - meta: A dictionary to store metadata.
        """
        self.target = None
        self.fd: io.TextIOWrapper = None

    def create_dir(self, dir: Optional[str] = None) -> str:
        """
        Create a directory.

        Args:
        - dir: The directory path.

        Returns:
        The created directory path.

        Raises:
        - Exception: If an error occurs while creating the directory.
        """
        if dir:
            try:
                os.makedirs(dir, exist_ok=True)
            except Exception as e:
                raise CreateDirectoryError("Failed to create directory: {}".format(dir))
        return dir

    def remove_dir(self, dir):
        if dir:
            try:
                os.rmdir(dir)
            except Exception as e:
                raise RemoveDirectoryError("Failed to remove directory: {}".format(dir))
        return dir

    def create_file(self, path: Optional[str] = None) -> str:
        """
        Create a file.

        Args:
        - path: The file path.

        Returns:
        The created file path.

        Raises:
        - Exception: If an error occurs while creating the file.
        """
        created = False
        if not path:
            now = datetime.now()
            year, month, day = now.year, now.month, now.day

            dir = os.path.join(
                "".join([os.getcwd().split("backend")[0], "backend"]),
                f"data/{year}/{month:02d}",
            )

            self.create_dir(dir)
            path = os.path.join(dir, f"{day:02d}.txt")

        if not os.path.exists(path):
            try:
                self.open(path, "x")
                self.write("")
                created = True
                # Log file creation
            finally:
                self.close()
        return path, created

    def delete_file(self, path):
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

    def set_target(self, path: Optional[str] = None) -> str:
        """
        Set the target file path for the database.

        If no target path is provided, a new file path is generated using the current date.

        Args:
        - path: The optional target file path.

        Returns:
        The target file path.

        Raises:
        - Exception: If an error occurs while creating the file.
        """
        self.close()  # For safety because fd doesn't correspond to target
        self.target = path
        return self.target

    def open(self, path: str = None, mode: str = "x") -> io.TextIOWrapper:
        """
        Open a file for reading or writing.

        Args:
        - path: The path to the file. if None, self.target is used
        - mode: The mode in which to open the file ('r' for reading, 'w' for writing, etc.).

        Returns:
        The file descriptor.

        Raises:
        - Exception: If an error occurs while opening the file.
        """
        if path:
            self.set_target(path)
        try:
            self.fd = open(self.target, mode)
        except Exception as e:
            raise FileOpenError("Error opening file: {}".format(self.target))
        return self.fd

    def close(self) -> None:
        """
        Close the currently open file.

        Raises:
        - Exception: If an error occurs while closing the file.
        """
        try:
            if self.fd:
                self.fd.close()
        except Exception as e:
            raise FileCloseError("Error while closing file: {}".format(self.target))
        self.fd = None

    def write(self, data: str) -> int:
        """
        Write data to the open file.

        Args:
        - data: The data to write to the file.

        Returns:
        - int: The number of bytes written(Approximatly)

        Raises:
        - Exception: If an error occurs while writing to the file.
        """
        try:
            if self.fd:
                self.fd.write(data)
        except Exception as e:
            raise FileWriteError("Error writing to file: {}".format(self.target))

        return len(data)

    def write_data_line(self, data: Dict[str, Any]) -> int:
        line = ",".join([f"{key}={value}" for key, value in data.items()])
        self.write(line + "\n")

    def readline(self) -> str:
        """
        Read a line from the open file.

        Returns:
        The read line.

        Raises:
        - Exception: If an error occurs while reading from the file.
        """
        line = None
        try:
            if self.fd:
                line = self.fd.readline()
        except Exception as e:
            raise FileReadError("Error reading line from file: {}".format(self.target))
        return line

    def readlines(self) -> List[str]:
        """
        Read all lines from the open file.

        Returns:
        The read line.

        Raises:
        - Exception: If an error occurs while reading from the file.
        """
        lines = []
        try:
            lines = self.fd.readlines()
        except Exception as e:
            raise FileReadError("Error reading lines from file: {}".format(self.target))
        return lines


class MetaDB(FileDB):
    metadata_lines: List[str] = []

    def __init__(self):
        """
        Initialize a MetaDB instance.

        Attributes:
        - meta: A dictionary to store metadata.
        """
        self.meta = {}
        super().__init__()

    def retrieve_metadata_lines(self, path: Optional[str] = None) -> List[str]:
        """
        Retrieve lines from a metadata file.

        Args:
        - path: The optional path to the metadata file.

        Returns:
        A list of lines from the metadata file.
        """
        if not path:
            path = self._get_metadata_path(path)
        try:
            self.open(path, "r")
            self.metadata_lines = [line.rstrip("\n") for line in super().readlines()]
        finally:
            self.close()
        return self.metadata_lines

    def update_metadata_lines(self, meta: Dict[str, Any] = {}) -> List[str]:
        """
        Update lines in the metadata file with provided metadata.

        Args:
        - meta: Key-value pairs to update in the metadata.

        Returns:
        The updated list of lines from the metadata file.
        """
        meta = meta or self.meta
        keys = set(meta.keys())
        for index, line in enumerate(self.metadata_lines):
            if not line.startswith("#") and line:
                datakey = line.split("=")[0]
                if datakey in keys:
                    self.metadata_lines[index] = "{}={}".format(datakey, meta[datakey])
                    keys.remove(datakey)
        for key in keys:
            self.metadata_lines.append("{}={}".format(key, meta[key]))
        return self.metadata_lines

    def retrieve_metadata(
        self, path: Optional[str] = None, meta: List[str] = []
    ) -> Dict[str, str]:
        """
        Retrieve metadata from a file.

        Args:
        - path: The optional path to the metadata file.
        - meta: Optional keys to retrieve from the metadata_lines.

        Returns:
        The retrieved metadata.

        Raises:
        - Exception: If an error occurs while retrieving the metadata.
        """

        lines = self.retrieve_metadata_lines(path)
        for line in lines:
            if not line.startswith("#") and "=" in line:
                key, val = [line.strip() for line in line.split("=")]
                if not meta or key in meta:
                    self.meta[key] = convert_to_int_or_leave_unchanged(val)
        return self.meta

    def save_metadata(
        self, path: Optional[str] = None, meta: Dict[str, Any] = {}
    ) -> None:
        """
        Save metadata to a file.

        The metadata is updated with the provided key-value pairs, and the updated metadata is saved to a file.

        Args:
        - path: The optional path to the metadata file.
        - meta: Key-value pairs to update in the metadata.

        Raises:
        - Exception: If an error occurs while saving the metadata.
        """
        if not path:
            path = self._get_metadata_path()

        if not self.create_file(path)[1]:
            self.retrieve_metadata_lines(path)
        try:
            self.open(path, "w")
            for line in self.update_metadata_lines(meta):
                self.write(line + "\n")
        finally:
            self.close()
        # Log save metadata

    def clear_metadata(self) -> None:
        """
        Clear the metadata stored in the instance.

        This method resets the metadata dictionary to an empty state.

        Returns:
        None
        """
        self.meta = {}

    def update_metadata(self, newmeta: Dict[str, str]) -> Dict[str, str]:
        """
        Update the metadata with the provided key-value pairs.

        Args:
        - newmeta: Key-value pairs to update in the metadata.

        Returns:
        The updated metadata.
        """
        if newmeta:
            self.meta.update(newmeta)
        return self.meta

    def readline(self, offset: int = None) -> str:
        """
        Read all lines from the open file.

        Args:
        - offset: Metadata to determine the file offset.

        Returns:
        The read line.

        Raises:
        - Exception: If an error occurs while reading from the file.
        """

        self.fd.seek(offset or int(self.meta.get("offset", 0)))
        line = super().readline()
        self.update_metadata({"offset": self.fd.tell()})
        return line

    def readlines(self, offset=None) -> List[str]:
        """
        Read all lines from the open file.

        Args:
        - offset: Metadata to determine the file offset.

        Returns:
        The list of read lines.
        """
        self.fd.seek(offset or int(self.meta.get("offset", 0)))
        lines = super().readlines()
        self.update_metadata({"offset": self.fd.tell()})
        return lines

    def _get_metadata_path(self, custom_path: Optional[str] = None) -> str:
        """
        Get the path to the metadata file.

        Args:
        - custom_path: The optional custom path to the metadata file.

        Returns:
        The path to the metadata file.
        """
        base_path = os.path.join(
            "".join([os.getcwd().split("backend")[0], "backend"]), "config"
        )
        return (
            os.path.join(base_path, custom_path)
            if custom_path
            else os.path.join(base_path, "meta.txt")
        )


def convert_to_int_or_leave_unchanged(value: str) -> Union[int, str]:
    """
    Attempt to convert a string to an integer. If successful, return the integer;
    otherwise, return the original string.

    Args:
    - value (str): The input string.

    Returns:
    - Union[int, str]: The converted integer or the original string.
    """
    if value.isdigit():
        return int(value)
    return value
