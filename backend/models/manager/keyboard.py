from models.db_engine.db import TempDB, FileDB
from pynput import keyboard
from .manager import Manager
from util import modify_data_to_dict
import signal


def sigint_handler(signal, frame):
    pass


def on_ctrl_c():
    print("ctrl-c on")
    manager = Manager.get_instance()
    manager.handle_command("START-CLOUD_TRANSFER")


def off_ctrl_c():
    print("ctrl-c off")
    manager = Manager.get_instance()
    manager.handle_command("STOP-CLOUD_TRANSFER")


def on_ctrl_s():
    print("ctrl-s on", flush=True)
    manager = Manager.get_instance()
    sensors = get_active_sensors()
    manager.handle_command("START-DATA_SAVING", *sensors)


def get_active_sensors(line: str = None):
    tmp_db = TempDB()
    path = tmp_db.get_tmp_db_path()
    activate_sensor = []
    if line is None:
        with FileDB(path, "r") as db:
            lines = db.readlines()
        line = lines[-1]

    data = modify_data_to_dict(line)
    for sensor, value in data.items():
        if value is not None:
            activate_sensor.append(sensor)
    return activate_sensor


def off_ctrl_s():
    print("ctrl-s off", flush=True)
    manager = Manager.get_instance()
    manager.handle_command("STOP-DATA_SAVING")


def on_ctrl_d():
    print("ctrl-d on")
    manager = Manager.get_instance()
    manager.handle_command("START-DATA_COLLECTION")


def off_ctrl_d():
    print("ctrl-d off")
    manager = Manager.get_instance()
    manager.handle_command("STOP-DATA_COLLECTION")


KEYS = {
    "ctrl_c": {"flag": 0, "functions": (on_ctrl_c, off_ctrl_c)},
    "ctrl_s": {"flag": 0, "functions": (on_ctrl_s, off_ctrl_s)},
    "ctrl_d": {"flag": 0, "functions": (on_ctrl_d, off_ctrl_d)},
}


def activate_helper(key: str):
    if flagnfunc := KEYS.get(key):
        flagnfunc.get("functions")[flagnfunc.get("flag")]()
        flagnfunc["flag"] = not flagnfunc["flag"]


def on_activate_c():
    activate_helper("ctrl_c")


def on_activate_s():
    activate_helper("ctrl_s")


def on_activate_d():
    activate_helper("ctrl_d")


class KeyboardInputHandler:
    """
    KeyboardInputHandler manages keyboard inputs and corresponding actions.

    It sets up global hotkeys to trigger actions based on keyboard shortcuts.
    """

    def __init__(self):
        """
        Initialize the KeyboardInputHandler instance.

        It sets up global hotkeys for specific keyboard shortcuts.
        """
        self.hotkeys = keyboard.GlobalHotKeys(
            {
                "<ctrl>+u": on_activate_c,
                "<ctrl>+q": on_activate_s,
                "<ctrl>+d": on_activate_d,
            }
        )

    def listen(self):
        """
        Listen for keyboard inputs and trigger corresponding actions.

        This method sets up signal handling for SIGINT and starts listening for keyboard inputs.
        """
        signal.signal(signal.SIGINT, sigint_handler)
        with self.hotkeys as hk:
            hk.join()
