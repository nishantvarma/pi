import ast
import os

from pathlib import Path

from pi.utils import cd


def exec_with_return(code, globals, locals):
    a = ast.parse(code)
    last_expression = None
    if a.body:
        if isinstance(a_last := a.body[-1], ast.Expr):
            last_expression = ast.unparse(a.body.pop())
        elif isinstance(a_last, ast.Assign):
            last_expression = ast.unparse(a_last.targets[0])
        elif isinstance(a_last, (ast.AnnAssign, ast.AugAssign)):
            last_expression = ast.unparse(a_last.target)
    exec(ast.unparse(a), globals, locals)
    if last_expression:
        return eval(last_expression, globals, locals)


class Folder():
    def __init__(self, dir):
        self.dir = dir

    def create_link(self, file, name=None):
        with cd(self.dir):
            link = os.path.relpath(file)
            os.symlink(link, name or os.path.basename(link))

    def create_file(self, name):
        Path.touch(os.path.join(self.dir, name))

    def create_folder(self, name):
        os.mkdir(os.path.join(self.dir, name))

    def get_files(self, hidden=False, pattern=None):
        files = sorted(os.listdir(self.dir))
        final = []
        for file in files:
            if not hidden and file.startswith("."):
                continue
            if pattern and pattern not in file:
                continue
            final.append(file)
        return final

    def get_file_type(self, file):
        with cd(self.dir):
            if os.path.islink(file):
                if os.path.exists(file):
                    return "active_link"
                else:
                    return "broken_link"
        path = os.path.join(self.dir, file)
        if os.path.isdir(path):
            return "folder"
        elif os.access(path, os.X_OK):
            return "executable"
        else:
            return "file"
