

import json
import os


class DB:
    _value: dict
    _store: str

    def __init__(self, store: str = "./db.json"):
        self._store = store
        if not os.path.exists(store):
            with open(store, "w") as f:
                f.write("{}")
                f.close()
        self._value = json.loads(open(store, "r").read())

    def save(self):
        json.dump(self._value, open(self._store, "w"))

    def use(self, workflow: str) -> dict:
        if self._value.get(workflow) == None:
            self._value[workflow] = {}
        return self._value[workflow]

