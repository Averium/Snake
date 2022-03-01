import json
import os


class PATH:
    ROOT = os.getcwd()
    DATA = os.path.join(ROOT, "data")
    LAYOUT = os.path.join(DATA, "layout.json")
    COLORS = os.path.join(DATA, "colors.json")
    SCORE = os.path.join(DATA, "score.json")
    SETTINGS = os.path.join(DATA, "settings.json")
    KEYBIND = os.path.join(DATA, "keybind.json")


class JsonData:

    def __init__(self, path, read_only=True):
        self._file = path
        self._data = {}
        self.load()
        self.read_only = read_only

    def load(self):
        with open(self._file, "r") as FILE:
            self._data = json.load(FILE)

        for key, value in self._data.items():
            setattr(self, key, value)

    def save(self):
        if self.read_only:
            print(f"WARNING: {self._file} is read only!")
        else:
            for key in self._data:
                self._data[key] = getattr(self, key)

            with open(self._file, "w") as FILE:
                json.dump(self._data, FILE, indent=2, sort_keys=False)


SETTINGS = JsonData(PATH.SETTINGS)
COLORS = JsonData(PATH.COLORS)
LAYOUT = JsonData(PATH.LAYOUT)
SCORE = JsonData(PATH.SCORE, read_only=False)
KEYS = JsonData(PATH.KEYBIND, read_only=False)
