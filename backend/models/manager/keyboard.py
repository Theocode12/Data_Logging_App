from pynput import keyboard
from .manager import Manager
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
    manager.handle_command(
        "START-DATA_SAVING",
        "longitude",
        "latitude",
        'altitude'
    )


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
    def __init__(self):
        self.hotkeys = keyboard.GlobalHotKeys(
            {
                "<ctrl>+u": on_activate_c,
                "<ctrl>+q": on_activate_s,
                "<ctrl>+d": on_activate_d,
            }
        )

    def listen(self):
        signal.signal(signal.SIGINT, sigint_handler)
        with self.hotkeys as hk:
            hk.join()
