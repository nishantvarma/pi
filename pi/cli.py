#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
from pathlib import Path

from blessed import Terminal

EDIT = "edit"
FUZZYEDIT = "fuzzyedit"
FUZZYOPEN = "fuzzyopen"
MARKS = ".config/pi/marks"
OPEN = "open"
SHELL = "rc"
TERM = "st"
VC = "v"


class FM:
    def __init__(self, path="."):
        self.t = Terminal()
        self.cwd = Path(path).resolve()
        self.files, self.clip, self.sel = [], [], set()
        self.cutting, self.hidden, self.cur = False, False, 0
        self.marks = Path.home() / MARKS
        self.marks.mkdir(parents=True, exist_ok=True)

    def run(self):
        os.chdir(self.cwd)
        t = self.t
        self.keys = {
            " ": ("Select", self.toggle),
            "*": ("Chmod +x", self.chmod),
            ".": ("Hidden", lambda: setattr(self, "hidden", not self.hidden)),
            "/": ("Search", self.search),
            "c": ("Copy", self.copy),
            "d": ("Delete", self.rm),
            "e": ("Edit", self.edit),
            "g": ("Marks", lambda: self.cd(self.marks)),
            "h": ("Help", self.help),
            "l": ("Link", self.link),
            "m": ("Mark", self.mark),
            "n": ("New file", self.touch),
            "N": ("New dir", self.mkdir),
            "o": ("Fuzzy open", self.fzopen),
            "p": ("Paste", self.paste),
            "q": ("Quit", self.quit),
            "r": ("Rename", self.rename),
            "s": ("Shell", self.sh),
            "v": ("VC", self.vc),
            "x": ("Cut", self.cut),
            "z": ("Fuzzy edit", self.fzedit),
            "~": ("Home", lambda: self.cd(Path.home())),
            "j": (None, lambda: self.mv(1)),
            "k": (None, lambda: self.mv(-1)),
            "KEY_DOWN": (None, lambda: self.mv(1)),
            "KEY_UP": (None, lambda: self.mv(-1)),
            "KEY_RIGHT": (None, self.enter),
            "KEY_LEFT": (None, lambda: self.cd(self.cwd.parent)),
            "KEY_ENTER": (None, self.enter),
            "\n": (None, self.enter),
        }
        try:
            with t.fullscreen(), t.cbreak(), t.hidden_cursor():
                while True:
                    self.ls()
                    self.draw()
                    key = t.inkey(timeout=1)
                    if not key:
                        continue
                    k = key.name or str(key)
                    if k in self.keys:
                        if self.keys[k][1]() == "quit":
                            break
                    elif key.isdigit():
                        self.jump(key)
        except KeyboardInterrupt:
            self.quit()

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
        self.out(t.home + t.clear)
        title = t.bold + self.tilde(self.cwd) + t.normal
        if self.sel:
            title += t.dim + f" [{len(self.sel)}]" + t.normal
        if self.clip:
            title += (
                t.dim
                + f" {'cut' if self.cutting else 'cp'}:{len(self.clip)}"
                + t.normal
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
        self.out(t.move_y(t.height - 1) + t.clear_eol)

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
        return str()

    def mv(self, d):
        if self.files:
            self.cur = max(0, min(len(self.files) - 1, self.cur + d))

    def toggle(self):
        if self.files:
            self.sel.symmetric_difference_update({self.files[self.cur]})

    def jump(self, first):
        t = self.t
        self.out(t.move_y(t.height - 1) + t.clear_eol + t.cnorm + first)
        buf = first
        while True:
            key = t.inkey(timeout=1)
            if not key:
                break
            if self.isesc(key):
                self.out(t.civis)
                return
            if self.isenter(key):
                break
            if key.isdigit():
                buf += key
                self.out(key)
            else:
                break
        self.out(t.civis)
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
            self.spawn(OPEN, str(p))

    def cd(self, p):
        self.cwd, self.cur = p.resolve(), 0
        os.chdir(self.cwd)
        self.sel.clear()

    def copy(self):
        self.yank(False)

    def cut(self):
        self.yank(True)

    def yank(self, cut):
        self.clip = self.targets()
        self.cutting = cut
        self.sel.clear()

    def paste(self):
        for src in self.clip:
            dst = self.cwd / src.name
            try:
                if self.cutting:
                    shutil.move(src, dst)
                elif src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except (OSError, shutil.Error):
                pass
        if self.cutting:
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
            self.spawn(EDIT, str(self.files[self.cur]))

    def fzedit(self):
        self.spawn(FUZZYEDIT)

    def fzopen(self):
        self.spawn(FUZZYOPEN)

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
        subprocess.Popen([TERM, "-e", SHELL])

    def vc(self):
        self.spawn(VC)

    def quit(self):
        t = self.t
        self.out(t.exit_fullscreen + t.normal_cursor + t.clear)
        return "quit"

    def help(self):
        t = self.t
        self.out(t.home + t.clear)
        print(t.bold + "Shortcuts" + t.normal + "\n")
        for k, (desc, _) in self.keys.items():
            if desc:
                print(f"  {t.yellow}{k:8}{t.normal} {desc}")
        print(f"\n  {t.dim}Press any key{t.normal}")
        t.inkey()

    def chmod(self):
        if self.files:
            p = self.files[self.cur]
            p.chmod(p.stat().st_mode ^ 0o111)

    def search(self):
        pat = self.prompt("/")
        if not pat:
            return
        pat = pat.lower()
        for i, f in enumerate(self.files):
            if pat in f.name.lower():
                self.cur = i
                return

    def link(self):
        if not self.clip:
            return
        for src in self.clip:
            dst = self.cwd / src.name
            if not dst.exists():
                dst.symlink_to(src)

    def spawn(self, *cmd):
        t = self.t
        self.out(t.exit_fullscreen + t.normal_cursor)
        os.system("stty sane")
        ret = subprocess.run(cmd)
        if ret.returncode:
            os.system("pause")
        os.system("stty -echo -icanon")
        self.out(t.enter_fullscreen + t.clear + t.civis)

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
        return str(), str()

    def prompt(self, msg):
        t = self.t
        self.out(t.move_y(t.height - 1) + t.clear_eol + t.cnorm + msg)
        buf = str()
        while True:
            key = t.inkey()
            if self.isesc(key):
                self.out(t.civis)
                return None
            if self.isenter(key):
                self.out(t.civis)
                return buf
            if self.isbs(key):
                if buf:
                    buf = buf[:-1]
                    self.out(t.move_left + " " + t.move_left)
            elif key.isprintable():
                buf += key
                self.out(key)

    def isesc(self, key):
        return key.name == "KEY_ESCAPE"

    def isenter(self, key):
        return key.name == "KEY_ENTER" or key == "\n"

    def isbs(self, key):
        return key.name == "KEY_BACKSPACE" or key == chr(127)

    def out(self, *args):
        print(*args, end=str(), flush=True)


if __name__ == "__main__":
    FM(sys.argv[1] if len(sys.argv) > 1 else ".").run()
