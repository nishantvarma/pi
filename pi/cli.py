#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
from pathlib import Path
from blessed import Terminal

EDIT = "edit"
FUZZYEDIT = "fuzzyedit"
MARKS = ".config/pi/marks"
OPEN = "open"
SHELL = "rc"


class FM:
    def __init__(self, path="."):
        self.t = Terminal()
        self.cwd = Path(path).resolve()
        self.files, self.clip, self.sel = [], [], set()
        self.cut, self.hidden, self.cur = False, False, 0
        self.marks = Path.home() / MARKS
        self.marks.mkdir(parents=True, exist_ok=True)

    def run(self):
        os.chdir(self.cwd)
        t = self.t
        keys = {
            "q": lambda: "quit",
            "j": lambda: self.mv(1),
            "k": lambda: self.mv(-1),
            "KEY_DOWN": lambda: self.mv(1),
            "KEY_UP": lambda: self.mv(-1),
            "l": self.enter,
            "KEY_RIGHT": self.enter,
            "KEY_ENTER": self.enter,
            "\n": self.enter,
            "h": lambda: self.cd(self.cwd.parent),
            "KEY_LEFT": lambda: self.cd(self.cwd.parent),
            "~": lambda: self.cd(Path.home()),
            "g": lambda: self.cd(self.marks),
            " ": self.toggle,
            ".": lambda: setattr(self, "hidden", not self.hidden),
            "c": self.copy,
            "x": self.snip,
            "p": self.paste,
            "d": self.rm,
            "m": self.mark,
            "e": self.edit,
            "n": self.touch,
            "N": self.mkdir,
            "r": self.rename,
            "s": self.sh,
        }
        with t.fullscreen(), t.cbreak(), t.hidden_cursor():
            while True:
                self.ls()
                self.draw()
                key = t.inkey(timeout=1)
                if not key:
                    continue
                k = key.name or str(key)
                if k in keys:
                    if keys[k]() == "quit":
                        break
                elif key.isdigit():
                    self.jump(key)

    def ls(self):
        try:
            self.files = sorted(
                [
                    f
                    for f in self.cwd.iterdir()
                    if self.hidden or not f.name.startswith(".")
                ],
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except PermissionError:
            self.files = []
        self.cur = min(self.cur, max(0, len(self.files) - 1))

    def draw(self):
        t = self.t
        print(t.home + t.clear, end="")
        title = t.bold + self.tilde(self.cwd) + t.normal
        if self.sel:
            title += t.dim + f" [{len(self.sel)}]" + t.normal
        if self.clip:
            title += (
                t.dim + f" {'cut' if self.cut else 'cp'}:{len(self.clip)}" + t.normal
            )
        print(title)
        h = t.height - 2
        off = self.scroll(h)
        for i, f in enumerate(self.files[off : off + h]):
            idx = off + i
            col, suf = self.style(f)
            bg = self.highlight(idx, f)
            print(f" {t.yellow}{idx + 1:2}{t.normal}  {bg}{col}{f.name}{suf}{t.normal}")
        if len(self.files) > h:
            print(t.dim + f" +{len(self.files) - h}" + t.normal)
        print(t.move_y(t.height - 1) + t.clear_eol, end="", flush=True)

    def scroll(self, h):
        if len(self.files) <= h:
            return 0
        return max(0, min(self.cur - h // 2, len(self.files) - h))

    def highlight(self, idx, f):
        t = self.t
        if idx == self.cur:
            return t.on_gray20
        if f in self.sel:
            return t.on_gray30
        return ""

    def mv(self, d):
        if self.files:
            self.cur = max(0, min(len(self.files) - 1, self.cur + d))

    def toggle(self):
        if self.files:
            self.sel.symmetric_difference_update({self.files[self.cur]})

    def jump(self, first):
        t = self.t
        print(
            t.move_y(t.height - 1) + t.clear_eol + t.cnorm + first, end="", flush=True
        )
        buf = first
        while True:
            key = t.inkey(timeout=1)
            if not key:
                break
            if self.is_esc(key):
                print(t.civis, end="", flush=True)
                return
            if self.is_enter(key):
                break
            if key.isdigit():
                buf += key
                print(key, end="", flush=True)
            else:
                break
        print(t.civis, end="", flush=True)
        if buf.isdigit():
            n = int(buf) - 1
            if 0 <= n < len(self.files):
                self.cur = n

    def enter(self):
        if not self.files:
            return
        p = self.files[self.cur]
        if p.is_dir():
            self.cd(p)
        else:
            with self.t.fullscreen():
                subprocess.run([OPEN, str(p)])

    def cd(self, p):
        self.cwd, self.cur = p.resolve(), 0
        os.chdir(self.cwd)
        self.sel.clear()

    def copy(self):
        self.clip = self.targets()
        self.cut = False
        self.sel.clear()

    def snip(self):
        self.clip = self.targets()
        self.cut = True
        self.sel.clear()

    def paste(self):
        for src in self.clip:
            dst = self.cwd / src.name
            try:
                if self.cut:
                    shutil.move(src, dst)
                elif src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except (OSError, shutil.Error):
                pass
        if self.cut:
            self.clip = []

    def rm(self):
        paths = self.targets()
        if not paths:
            return
        self.prompt(f"rm {' '.join(p.name for p in paths)}? ")
        if self.t.inkey() != "y":
            return
        for p in paths:
            try:
                shutil.rmtree(p) if p.is_dir() else p.unlink()
            except OSError:
                pass
        self.sel.clear()

    def mark(self):
        default = self.cwd.name
        name = self.prompt(f"mark [{default}]: ")
        if name is None:
            return
        name = name or default
        (self.marks / name).unlink(missing_ok=True)
        (self.marks / name).symlink_to(self.cwd)

    def edit(self):
        if self.files and self.files[self.cur].is_file():
            with self.t.fullscreen():
                subprocess.run([EDIT, str(self.files[self.cur])])
        else:
            with self.t.fullscreen():
                subprocess.run([FUZZYEDIT])

    def mkdir(self):
        name = self.prompt("mkdir: ")
        if name:
            (self.cwd / name).mkdir(exist_ok=True)

    def touch(self):
        name = self.prompt("touch: ")
        if name:
            (self.cwd / name).touch()

    def rename(self):
        if not self.files:
            return
        p = self.files[self.cur]
        name = self.prompt(f"mv {p.name}: ")
        if name:
            p.rename(self.cwd / name)

    def sh(self):
        subprocess.Popen(["st", "-e", SHELL])

    def targets(self):
        if self.sel:
            return list(self.sel)
        if self.files:
            return [self.files[self.cur]]
        return []

    def tilde(self, p):
        try:
            return "~/" + str(p.relative_to(Path.home()))
        except ValueError:
            return str(p)

    def style(self, p):
        t = self.t
        if p.is_symlink():
            return t.cyan, "@"
        if p.is_dir():
            return t.blue, "/"
        if os.access(p, os.X_OK):
            return t.green, "*"
        return "", ""

    def prompt(self, msg):
        t = self.t
        print(t.move_y(t.height - 1) + t.clear_eol + t.cnorm + msg, end="", flush=True)
        buf = ""
        while True:
            key = t.inkey()
            if self.is_esc(key):
                print(t.civis, end="", flush=True)
                return None
            if self.is_enter(key):
                print(t.civis, end="", flush=True)
                return buf
            if self.is_bs(key):
                if buf:
                    buf = buf[:-1]
                    print(t.move_left + " " + t.move_left, end="", flush=True)
            elif key.isprintable():
                buf += key
                print(key, end="", flush=True)

    def is_esc(self, key):
        return key.name == "KEY_ESCAPE"

    def is_enter(self, key):
        return key.name == "KEY_ENTER" or key == "\n"

    def is_bs(self, key):
        return key.name == "KEY_BACKSPACE" or key == chr(127)


if __name__ == "__main__":
    FM(sys.argv[1] if len(sys.argv) > 1 else ".").run()
