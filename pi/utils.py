import os
import sys

from contextlib import contextmanager
from tkinter import messagebox


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
        os.execl(python, python, "-m", "pi.pi")


def quit(event=None):
    if messagebox.askyesno("Quit", "Are you sure?"):
        sys.exit(0)
