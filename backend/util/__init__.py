from typing import Union
import os
import subprocess


def get_base_path():
    return "".join([os.getcwd().split("backend")[0], "backend"])


def is_internet_connected():
    try:
        subprocess.check_output(["timeout", "1", "ping", "-c", "1", "google.com"])
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


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
