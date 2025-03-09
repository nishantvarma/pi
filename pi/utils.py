import os

from contextlib import contextmanager


@contextmanager
def cd(dir):
    cwd = os.getcwd()
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(cwd)
