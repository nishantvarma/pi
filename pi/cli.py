#!/usr/bin/env python

import os
import readline
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

from blessed import Terminal

EDIT = "edit"
FUZZYEDIT = "fzedit"
FUZZYOPEN = "fzopen"
MARKS = ".config/pi/marks"
OPEN = "open"
SHELL = ["rlwrap", "--always-readline", "-c", "rc"]
TERM = "st"
VC = "v"


class FM:
    # lifecycle
    def __init__(self, path="."):
        self.t = Terminal()
        self.cwd = Path(path).resolve()
        self.last = None
        self.files, self.clip, self.sel = [], [], set()
        self.cutting, self.hidden, self.idx = False, False, 0
        self.pat = str()
        self.marks = Path.home() / MARKS
        self.marks.mkdir(parents=True, exist_ok=True)

    def run(self):
        os.chdir(self.cwd)
        self.title(f"pi:{self.cwd}")
        t = self.t
        self.keys = {
            "a": ("Add file", lambda: self.create("touch", Path.touch)),
            "A": ("Add dir", lambda: self.create("mkdir", Path.mkdir)),
            "c": ("Copy", self.copy),
            "d": ("Delete", self.rm),
            "e": ("Edit", self.edit),
            "g": ("Goto", self.goto),
            "h": ("Help", self.help),
            "j": (None, lambda: self.mv(1)),
            "k": (None, lambda: self.mv(-1)),
            "l": ("Link", self.link),
            "m": ("Mark", self.mark),
            "n": ("Next", self.next),
            "N": ("Prev", self.prev),
            "o": ("Fuzzy open", lambda: self.spawn(FUZZYOPEN)),
            "p": ("Paste", self.paste),
            "q": ("Quit", self.quit),
            "r": ("Rename", self.rename),
            "s": ("Shell", self.sh),
            "t": ("Toggle", self.toggle),
            "u": ("Unclip", lambda: setattr(self, "clip", [])),
            "v": ("VC", self.vc),
            "V": ("Git gui", lambda: self.spawn("git", "gui")),
            "x": ("Cut", self.cut),
            "z": ("Fuzzy edit", lambda: self.spawn(FUZZYEDIT)),
            "*": ("Chmod +x", self.chmod),
            ".": ("Hidden", lambda: setattr(self, "hidden", not self.hidden)),
            "/": ("Search", self.search),
            "`": ("Marks", self.gomarks),
            "~": ("Home", lambda: self.cd(Path.home())),
            "\n": (None, self.enter),
            "KEY_DOWN": (None, lambda: self.mv(1)),
            "KEY_ENTER": (None, self.enter),
            "KEY_LEFT": (None, lambda: self.cd(self.cwd.parent)),
            "KEY_RIGHT": (None, self.enter),
            "KEY_TAB": (None, lambda: self.cd(self.last) if self.last else None),
            "KEY_UP": (None, lambda: self.mv(-1)),
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
                        if self.keys[k][1]():
                            break
                    elif key.isdigit():
                        self.jump(key)
        except KeyboardInterrupt:
            self.quit()

    # core
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
        self.idx = max(0, min(len(self.files) - 1, self.idx))

    def draw(self):
        t = self.t
        self.out(t.home)
        title = self.bold(self.tilde(self.cwd))
        if self.sel:
            title += self.dim(f" [{len(self.sel)}]")
        if self.clip:
            mode = "cut" if self.cutting else "cp"
            title += self.dim(f" {mode}:{len(self.clip)}")
        print(title + t.clear_eol)
        h = t.height - 2
        if len(self.files) > h:
            h -= 1
        off = self.scroll(h)
        visible = self.files[off : off + h]
        for i, f in enumerate(visible, off):
            print(self.row(i, f) + t.clear_eol)
        extra = h - len(visible)
        if len(self.files) > h:
            hidden = len(self.files) - h
            print(self.dim(f" +{hidden}") + t.clear_eol)
            extra -= 1
        for _ in range(extra):
            print(t.clear_eol)
        self.status()

    # public
    def cd(self, p):
        self.last = self.cwd
        self.cwd, self.idx = p.resolve(), 0
        os.chdir(self.cwd)
        self.title(f"pi:{self.cwd}")
        self.sel.clear()

    def chmod(self):
        if self.cur:
            self.cur.chmod(self.cur.stat().st_mode ^ 0o111)

    def copy(self):
        self.yank(False)

    def cut(self):
        self.yank(True)

    def edit(self):
        if self.cur and self.cur.is_file():
            self.spawn(EDIT, str(self.cur))

    def enter(self):
        if not self.cur:
            return
        if self.cur.is_dir():
            self.cd(self.cur)
        else:
            self.spawn(OPEN, str(self.cur))

    def goto(self):
        with self.tty():
            readline.parse_and_bind("tab: complete")
            try:
                path = input("goto: ")
            except (EOFError, KeyboardInterrupt):
                return
        if path:
            p = Path(path).expanduser().resolve()
            if p.is_dir():
                self.cd(p)
            elif p.is_file():
                self.spawn(OPEN, str(p))

    def gomarks(self):
        self.cd(self.marks)
        self.ls()
        self.draw()
        self.search()

    def help(self):
        self.out(self.t.home + self.t.clear)
        print(self.bold("Shortcuts") + "\n")
        for k, (desc, _) in self.keys.items():
            if desc:
                key = self.yellow(f"{k:8}")
                print(f"  {key} {desc}")
        print(self.dim("\n  Press any key"))
        self.t.inkey()

    def jump(self, first):
        t = self.t
        self.status(first, cursor=True)
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
                self.idx = n

    def link(self):
        if not self.clip:
            return
        for src in self.clip:
            dst = self.cwd / src.name
            if not dst.exists():
                dst.symlink_to(src)

    def mark(self):
        default = self.cwd.name
        name = self.prompt(f"mark [{default}]: ")
        if name is None:
            return
        name = name or default
        (self.marks / name).unlink(missing_ok=True)
        (self.marks / name).symlink_to(self.cwd)

    def mv(self, d):
        if self.files:
            self.idx = max(0, min(len(self.files) - 1, self.idx + d))

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

    def rename(self):
        if not self.cur:
            return
        name = self.prompt(f"mv {self.cur.name}: ")
        if name:
            self.cur.rename(self.cwd / name)

    def rm(self):
        paths = self.targets()
        if not paths:
            return
        names = " ".join(p.name for p in paths)
        self.status(f"rm {names}? ")
        if self.t.inkey() != "y":
            return
        for p in paths:
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
            except OSError:
                pass
        self.sel.clear()

    def search(self):
        pat = self.prompt("/")
        if not pat:
            return
        self.pat = pat.lower()
        self.next()

    def next(self):
        self.find(1)

    def prev(self):
        self.find(-1)

    def sh(self):
        subprocess.Popen([TERM, "-e", *SHELL])

    def toggle(self):
        if self.cur:
            self.sel ^= {self.cur}

    def quit(self):
        self.out(self.t.exit_fullscreen + self.t.normal_cursor + self.t.clear)
        return True

    def vc(self):
        self.spawn(VC)

    # internals
    @property
    def cur(self):
        return self.files[self.idx] if self.files else None

    def find(self, d):
        if not self.pat or not self.files:
            return
        for i in range(1, len(self.files) + 1):
            idx = (self.idx + d * i) % len(self.files)
            if self.pat in self.files[idx].name.lower():
                self.idx = idx
                return

    def create(self, label, fn):
        name = self.prompt(f"{label}: ")
        if name:
            fn(self.cwd / name)

    def highlight(self, idx, f):
        if idx == self.idx:
            return self.t.on_gray20
        if f in self.sel:
            return self.t.on_gray30
        return str()

    def isesc(self, key):
        return key.name == "KEY_ESCAPE"

    def isenter(self, key):
        return key.name == "KEY_ENTER" or key == "\n"

    def isbs(self, key):
        return key.name == "KEY_BACKSPACE" or key == chr(127)

    def prompt(self, msg):
        t = self.t
        self.status(msg, cursor=True)
        buf = str()
        while True:
            key = t.inkey()
            if self.isesc(key) or key.name == "KEY_DOWN":
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

    def row(self, i, f):
        fmt, suf = self.style(f)
        bg = self.highlight(i, f)
        num = self.yellow(f"{i + 1:2}")
        name = fmt(f.name + suf)
        return f" {num}  {bg}{name}"

    def scroll(self, h):
        if len(self.files) <= h:
            return 0
        return max(0, min(self.idx - h // 2, len(self.files) - h))

    @contextmanager
    def tty(self):
        t = self.t
        self.out(t.exit_fullscreen + t.clear + t.normal_cursor)
        os.system("stty sane")
        try:
            yield
        finally:
            os.system("stty -echo -icanon")
            self.out(t.enter_fullscreen + t.clear + t.civis)

    def spawn(self, *cmd):
        with self.tty():
            ret = subprocess.run(cmd)
            if ret.returncode:
                os.system("pause")

    def style(self, p):
        if p.is_symlink():
            return self.cyan, "@"
        if p.is_dir():
            return self.blue, "/"
        if os.access(p, os.X_OK):
            return self.green, "*"
        return self.plain, str()

    def targets(self):
        if self.sel:
            return list(self.sel)
        if self.cur:
            return [self.cur]
        return []

    def tilde(self, p):
        try:
            return "~/" + str(p.relative_to(Path.home()))
        except ValueError:
            return str(p)

    def yank(self, cut):
        self.clip = self.targets()
        self.cutting = cut
        self.sel.clear()

    # formatting
    def out(self, *args):
        print(*args, end=str(), flush=True)

    def status(self, msg=str(), cursor=False):
        cur = self.t.cnorm if cursor else str()
        self.out(self.t.move_y(self.t.height - 1) + self.t.clear_eol + cur + msg)

    def title(self, s):
        self.out(f"{chr(27)}]2;{s}{chr(7)}")

    def bold(self, s):
        return self.t.bold + s + self.t.normal

    def dim(self, s):
        return self.t.dim + s + self.t.normal

    def yellow(self, s):
        return self.t.yellow + s + self.t.normal

    def cyan(self, s):
        return self.t.cyan + s + self.t.normal

    def blue(self, s):
        return self.t.blue + s + self.t.normal

    def green(self, s):
        return self.t.green + s + self.t.normal

    def plain(self, s):
        return s + self.t.normal


if __name__ == "__main__":
    FM(sys.argv[1] if sys.argv[1:] else ".").run()
