import json
from pathlib import Path

BOOKS_FILE = Path("books_data.json")
CONFIG_FILE = Path("config.json")

def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")

def load_books():
    return load_json(BOOKS_FILE, {"read_later": [], "read_books": []})

def save_books(books):
    save_json(BOOKS_FILE, books)

def load_config():
    default = {"theme": "dark_teal.xml", "font": "Arial", "font_size": 10}
    return load_json(CONFIG_FILE, default)

def save_config(cfg):
    save_json(CONFIG_FILE, cfg)