import os
import sys

from contextlib import contextmanager
from pathlib import Path
from tkinter import messagebox

STATE = Path.home() / ".config" / "pi" / "state"


@contextmanager
def cd(dir):
    cwd = os.getcwd()
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(cwd)


def restart(event=None):
    if messagebox.askyesno("Restart", "Are you sure?"):
        python = sys.executable
        os.execl(python, python, "-m", "pi.main")


def quit(event=None):
    if messagebox.askyesno("Quit", "Are you sure?"):
        sys.exit(0)


def save_state(tabs):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text("\n".join(tabs))


def load_state():
    if STATE.exists():
        return [p for p in STATE.read_text().split("\n") if p]
    return []
