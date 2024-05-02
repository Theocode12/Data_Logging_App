from pynput import keyboard


def on_ctrl_c():
    print('ctrl-c on')


def off_ctrl_c():
    print('ctrl-c off')


def on_ctrl_s():
    print('ctrl-s on')


def off_ctrl_s():
    print('ctrl-s off')


def on_ctrl_d():
    print('ctrl-d on')


def off_ctrl_d():
    print('ctrl-d off')


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
    print("<ctrl>+c pressed")
    activate_helper('ctrl_c')


def on_activate_s():
    print("<ctrl>+s pressed")
    activate_helper('ctrl_s')


def on_activate_d():
    print("<ctrl>+d pressed")
    activate_helper('ctrl_d')


class KeyboardInputHandler:
    def __init__(self):
        self.hotkeys = keyboard.GlobalHotKeys(
            {
                "<ctrl>+c": on_activate_c,
                "<ctrl>+s": on_activate_s,
                "<ctrl>+d": on_activate_d,
            }
        )

    def listen(self):
        with self.hotkeys as hk:
            hk.join()
