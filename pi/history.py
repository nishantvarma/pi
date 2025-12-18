import os

HISTORY_FILE = os.path.expanduser("~/.config/pi/history")
MAX_SIZE = 1000


def add(path):
    path = os.path.abspath(path)
    history = get_all()
    if path in history:
        history.remove(path)
    history.insert(0, path)
    history = history[:MAX_SIZE]
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(history))


def get_all():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def clear():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
