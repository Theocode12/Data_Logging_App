import os
import subprocess


def get_base_path():
    return os.path.join("".join([os.getcwd().split("backend")[0], "backend"]))


def is_internet_connected():
    try:
        subprocess.check_output(["timeout", "1", "ping", "-c", "1", "google.com"])
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
