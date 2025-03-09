import os
import pytest
import shutil

from pi.core import Folder
from pi.utils import cd


@pytest.fixture()
def folder():
    os.mkdir("folder")
    yield
    shutil.rmtree("folder")


class TestFolder():
    def test_get_files(self, folder):
        f = Folder("folder")
        f.create_file("file")
        f.create_folder("folder")
        f.create_file(os.path.join("folder", "file"))
        f.create_link(os.path.join("folder", "file"), name="link")
        assert f.get_file_type("file") == "file"
        assert f.get_file_type("folder") == "folder"
        assert f.get_file_type("link") == "active_link"
