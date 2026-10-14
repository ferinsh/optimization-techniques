"""JSON settings helpers; current app persistence is preserved in ui/app.py."""
import json
import os

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    os.replace(temporary_path, path)

def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
