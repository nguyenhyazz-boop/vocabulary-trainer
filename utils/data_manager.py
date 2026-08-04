import json

DATA_FILE = "data.json"


def load_data():
    """Đọc toàn bộ dữ liệu."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    """Lưu dữ liệu."""

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )