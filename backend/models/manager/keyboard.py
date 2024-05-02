from pynput import keyboard


def on_ctrl_c():
    pass


def off_ctrl_c():
    pass


def on_ctrl_s():
    pass


def off_ctrl_s():
    pass


def on_ctrl_d():
    pass


def off_ctrl_d():
    pass


KEYS = {
    "ctrl_c": {"flag": 0, "functions": (on_ctrl_c, off_ctrl_c)},
    "ctrl_s": {"flag": 0, "functions": (on_ctrl_s, off_ctrl_s)},
    "ctrl_d": {"flag": 0, "functions": (on_ctrl_d, off_ctrl_d)},
}


def on_activate_c():
    print("<ctrl>+<alt>+c pressed")
    if flagnfunc := KEYS.get("ctrl_c"):
        flagnfunc.get("functions")[flagnfunc.get("flag")]
        flagnfunc["flag"] = not flagnfunc["flag"]


def on_activate_s():
    print("<ctrl>+<alt>+s pressed")
    if flagnfunc := KEYS.get("ctrl_s"):
        flagnfunc.get("functions")[flagnfunc.get("flag")]
        flagnfunc["flag"] = not flagnfunc["flag"]


def on_activate_d():
    print("<ctrl>+<alt>+s pressed")
    if flagnfunc := KEYS.get("ctrl_d"):
        flagnfunc.get("functions")[flagnfunc.get("flag")]
        flagnfunc["flag"] = not flagnfunc["flag"]


class KeyboardInputHandler:
    def __init__(self):
        self.kb = keyboard.GlobalHotKeys(
            {
                "<ctrl>+c": on_activate_c,
                "<ctrl>+s": on_activate_s,
                "<ctrl>+d": on_activate_d,
            }
        )

    def listen(self):
        with self.kb:
            self.kb.join()
