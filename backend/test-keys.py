#!.venv/bin/python3

# from pynput import keyboard

# def on_activate_h():
#     print('<ctrl>+<alt>+h pressed')

# def on_activate_i():
#     print('<ctrl>+<alt>+i pressed')

# with keyboard.GlobalHotKeys({
#         '<ctrl>+<alt>+h': on_activate_h,
#         '<ctrl>+<alt>+i': on_activate_i}) as h:
#     h.join()

from models.manager.keyboard import KeyboardInputHandler

k = KeyboardInputHandler()
k.listen()
