import json
import os
from collections import deque


class ActionStore:
    def __init__(self, max_len=5000, save_path="data/actions.jsonl"):
        self.data = deque(maxlen=max_len)
        self.save_path = save_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

    def add(self, action):
        self.data.append(action)
        if len(self.data) % 50 == 0:
            self.save()

    def get_last(self, n):
        return list(self.data)[-n:]

    def __len__(self):
        return len(self.data)

    def save(self):
        with open(self.save_path, "w") as f:
            for a in self.data:
                f.write(json.dumps(a) + "\n")

