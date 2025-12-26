#!/usr/bin/env python3

import glob
import os
import readline
import shutil
import subprocess
import sys
from pathlib import Path

from pick import pick

ESC = "\033["
BLUE = ESC + "34m"
GREEN = ESC + "32m"
CYAN = ESC + "36m"
YELLOW = ESC + "33m"
DIM = ESC + "2m"
BOLD = ESC + "1m"
RED = ESC + "31m"
RESET = ESC + "0m"


def style(p):
    if p.is_symlink():
        return CYAN, "@"
    if p.is_dir():
        return BLUE, "/"
    if os.access(p, os.X_OK):
        return GREEN, "*"
    return "", ""


def tildify(p):
    try:
        return "~/" + str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)


def shell(cmd):
    r = subprocess.run(cmd, shell=True, executable="rc")
    print(f"{GREEN}·{RESET}" if r.returncode == 0 else f"{RED}·{RESET}")
    input()


class FM:
    def __init__(self, path="."):
        self.cwd = Path(path).resolve()
        self.prev = self.cwd
        self.files = []
        self.clip = []
        self.sel = set()
        self.cut = False
        self.hidden = False
        self.marks = Path.home() / ".config/pi/marks"
        self.marks.mkdir(parents=True, exist_ok=True)
        readline.set_completer(lambda t, s: (glob.glob(os.path.expanduser(t) + "*") + [None])[s])
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")

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

    def draw(self):
        print("\033[H\033[J", end=str())
        title = f"{BOLD}{tildify(self.cwd)}{RESET}"
        if self.sel:
            title += f" {DIM}sel:{len(self.sel)}{RESET}"
        if self.clip:
            names = ", ".join(p.name for p in self.clip[:3])
            if len(self.clip) > 3:
                names += f" +{len(self.clip) - 3}"
            mode = "cut" if self.cut else "copy"
            title += f" {DIM}({mode}: {names}){RESET}"
        print(title)
        print()

        h = shutil.get_terminal_size().lines - 4
        for i, f in enumerate(self.files[:h], 1):
            col, suf = style(f)
            mark = "* " if f in self.sel else "  "
            print(f"{YELLOW}{i:3}{RESET} {mark}{col}{f.name}{suf}{RESET}")
        if len(self.files) > h:
            print(f"    {DIM}+{len(self.files) - h} more{RESET}")

    def go(self, n):
        if 1 <= n <= len(self.files):
            p = self.files[n - 1]
            if p.is_dir():
                self.cd(p)
            else:
                subprocess.run(["open", str(p)])

    def go_name(self, name):
        if name.startswith(("~", "/")):
            p = Path(os.path.expanduser(name))
        else:
            p = self.cwd / name
        if p.is_dir():
            self.cd(p.resolve())
            return True
        elif p.is_file():
            subprocess.run(["open", str(p)])
            return True
        return False

    def paths(self, args):
        out = []
        for a in args:
            try:
                n = int(a)
                if 1 <= n <= len(self.files):
                    out.append(self.files[n - 1])
            except ValueError:
                p = self.cwd / a
                if p.exists():
                    out.append(p)
        return out

    def run(self):
        os.chdir(self.cwd)
        cmds = {
            "..": lambda a: self.cd(self.cwd.parent),
            "b": lambda a: self.cd(self.cwd.parent),
            "~": lambda a: self.cd(Path.home()),
            "h": lambda a: setattr(self, "hidden", not self.hidden),
            "e": self.edit,
            "o": self.open,
            "c": self.yank,
            "x": lambda a: self.yank(a, cut=True),
            "p": lambda a: self.paste(),
            "d": self.delete,
            "r": self.rename,
            "n": self.touch,
            "m": self.mkdir,
            "l": lambda a: None,
            "g": self.go_mark,
            "s": self.select,
            "ss": lambda a: self.sel.clear(),
            "q": lambda a: sys.exit(0),
            "?": lambda a: self.help(cmds),
        }
        while True:
            self.ls()
            self.draw()
            try:
                line = input("; ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not line:
                self.cd(self.prev)
            elif line.isdigit():
                self.go(int(line))
            elif line.startswith("!"):
                shell(line[1:])
            elif line.split()[0] in cmds:
                parts = line.split()
                cmds[parts[0]](parts[1:])
            elif self.go_name(line.split()[0]):
                pass
            else:
                shell(line)

    def cd(self, p):
        if p != self.cwd:
            self.prev = self.cwd
        self.cwd = p
        os.chdir(p)
        self.sel.clear()

    def edit(self, args):
        if not args:
            subprocess.run(["fuzzyedit"])
            return
        for p in self.paths(args):
            subprocess.run(["edit", str(p)])

    def open(self, args):
        if not args:
            subprocess.run(["fuzzyopen"])
            return
        for p in self.paths(args):
            if p.is_dir():
                self.cd(p)
            else:
                subprocess.run(["open", str(p)])

    def select(self, args):
        if not args:
            if not self.files:
                return
            names = [f.name for f in self.files]
            selected = pick(names, multiselect=True, min_selection_count=0)
            self.sel.clear()
            for name, idx in selected:
                self.sel.add(self.files[idx])
            return
        for p in self.paths(args):
            if p in self.sel:
                self.sel.remove(p)
            else:
                self.sel.add(p)

    def yank(self, args, cut=False):
        self.clip = self.paths(args) if args else list(self.sel)
        self.cut = cut
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
            except Exception as e:
                print(f"{RED}{e}{RESET}")
        if self.cut:
            self.clip = []

    def delete(self, args):
        paths = self.paths(args) if args else list(self.sel)
        if not paths:
            return
        self.sel.clear()
        names = " ".join(p.name for p in paths)
        if input(f"rm {names}? ").lower() != "y":
            return
        for p in paths:
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
            except Exception as e:
                print(f"{RED}{e}{RESET}")

    def rename(self, args):
        if len(args) >= 2:
            paths = self.paths([args[0]])
            if paths:
                try:
                    paths[0].rename(self.cwd / args[1])
                except Exception as e:
                    print(f"{RED}{e}{RESET}")

    def touch(self, args):
        for name in args:
            (self.cwd / name).touch()

    def mkdir(self, args):
        for name in args:
            (self.cwd / name).mkdir(exist_ok=True)

    def go_mark(self, args):
        if not args:
            self.cd(self.marks)
            return
        if args[0].startswith("."):
            name = args[0][1:] or self.cwd.name
            mark = self.marks / name
            mark.unlink(missing_ok=True)
            mark.symlink_to(self.cwd)
            return
        mark = self.marks / args[0]
        if mark.exists():
            self.cd(mark.resolve())

    def help(self, cmds):
        print(" ".join(f"{BOLD}{k}{RESET}" for k in cmds))
        input()


if __name__ == "__main__":
    FM(sys.argv[1] if len(sys.argv) > 1 else ".").run()
