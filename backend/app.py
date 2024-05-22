#!.venv/bin/python3
from models.manager.keyboard import KeyboardInputHandler

if __name__ == "__main__":
    keyboard = KeyboardInputHandler()
    keyboard.listen()
