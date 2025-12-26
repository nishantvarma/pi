#!/usr/bin/env python3

import glob
import os
import readline
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

con = Console()


class FM:
    def __init__(self, path="."):
        self.cwd = Path(path).resolve()
        self.files = []
        self.clip = []
        self.cut = False
        self.hidden = False
        self.hist = Path.home() / ".config/pi/history"
        self.hist.parent.mkdir(parents=True, exist_ok=True)
        self._init_readline()

    def _init_readline(self):
        try:
            readline.read_history_file(self.hist)
        except FileNotFoundError:
            pass
        readline.set_completer(
            lambda t, s: (glob.glob(os.path.expanduser(t) + "*") + [None])[s]
        )
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")

    def _style(self, p):
        if p.is_symlink():
            return "cyan", "@"
        if p.is_dir():
            return "blue", "/"
        if os.access(p, os.X_OK):
            return "green", "*"
        return "white", ""

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
        con.clear()
        t = Table(show_header=False, box=None, padding=(0, 1))
        t.add_column(style="yellow", width=3, justify="right")
        t.add_column()

        h = con.size.height - 5
        for i, f in enumerate(self.files[:h], 1):
            style, suf = self._style(f)
            t.add_row(str(i), f"[{style}]{f.name}{suf}[/{style}]")
        if len(self.files) > h:
            t.add_row("", f"[dim]+{len(self.files) - h} more[/dim]")

        try:
            path = "~/" + str(self.cwd.relative_to(Path.home()))
        except ValueError:
            path = str(self.cwd)
        title = f"[bold]{path}[/bold]"
        if self.clip:
            names = ", ".join(p.name for p in self.clip[:3])
            if len(self.clip) > 3:
                names += f" +{len(self.clip) - 3}"
            mode = "cut" if self.cut else "copy"
            title += f" [dim]({mode}: {names})[/dim]"

        con.print(
            Panel(
                t, title=title, title_align="left", border_style="dim", padding=(0, 1)
            )
        )

    def go(self, n):
        if 1 <= n <= len(self.files):
            p = self.files[n - 1]
            if p.is_dir():
                self._cd(p)
            else:
                subprocess.run(["open", str(p)])

    def go_name(self, name):
        if name.startswith(("~", "/")):
            p = Path(os.path.expanduser(name))
        else:
            p = self.cwd / name
        if p.is_dir():
            self._cd(p.resolve())
            return True
        elif p.is_file():
            subprocess.run(["open", str(p)])
            return True
        return False

    def nums(self, args):
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
        self.ls()
        cmds = {
            "..": lambda a: self.go_up(),
            "b": lambda a: self.go_up(),
            "back": lambda a: self.go_up(),
            "~": lambda a: self.go_home(),
            "h": lambda a: self.toggle_hidden(),
            "e": lambda a: self.edit(a),
            "edit": lambda a: self.edit(a),
            "o": lambda a: self.open(a),
            "open": lambda a: self.open(a),
            "c": lambda a: self.yank(a),
            "cp": lambda a: self.yank(a),
            "x": lambda a: self.yank(a, cut=True),
            "v": lambda a: self.paste(),
            "d": lambda a: self.delete(a),
            "rm": lambda a: self.delete(a),
            "r": lambda a: self.rename(a),
            "mv": lambda a: self.rename(a),
            "n": lambda a: self.touch(a),
            "touch": lambda a: self.touch(a),
            "m": lambda a: self.mkdir(a),
            "mkdir": lambda a: self.mkdir(a),
            "l": lambda a: self.ls(),
            "ls": lambda a: self.ls(),
            "f": lambda a: self.search(),
            "q": lambda a: sys.exit(0),
            "quit": lambda a: sys.exit(0),
            "?": lambda a: self.help(cmds),
        }
        while True:
            self.draw()
            try:
                line = input("; ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                continue

            if line.isdigit():
                self.go(int(line))
                self.ls()
                continue

            if line.startswith("!"):
                subprocess.run(line[1:], shell=True)
                con.print("[dim]·[/dim]")
                input()
                self.ls()
                continue

            parts = line.split()
            cmd, args = parts[0], parts[1:]

            if cmd in cmds:
                cmds[cmd](args)
                self.ls()
                continue

            if self.go_name(cmd):
                self.ls()
                continue

            subprocess.run(line, shell=True)
            con.print("[dim]·[/dim]")
            input()
            self.ls()

        readline.write_history_file(self.hist)

    def _cd(self, p):
        self.cwd = p
        os.chdir(p)

    def go_up(self):
        if self.cwd.parent != self.cwd:
            self._cd(self.cwd.parent)

    def go_home(self):
        self._cd(Path.home())

    def toggle_hidden(self):
        self.hidden = not self.hidden

    def edit(self, args):
        if not args:
            subprocess.run(["fuzzyedit"])
            return
        for p in self.nums(args):
            subprocess.run(["edit", str(p)])

    def open(self, args):
        if not args:
            subprocess.run(["fuzzyopen"])
            return
        for p in self.nums(args):
            if p.is_dir():
                self._cd(p)
            else:
                subprocess.run(["open", str(p)])

    def yank(self, args, cut=False):
        self.clip = self.nums(args)
        self.cut = cut

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
                con.print(f"[red]{e}[/red]")
        if self.cut:
            self.clip = []

    def delete(self, args):
        paths = self.nums(args)
        if not paths:
            return
        names = " ".join(p.name for p in paths)
        if input(f"rm {names}? ").lower() == "y":
            for p in paths:
                try:
                    if p.is_dir():
                        shutil.rmtree(p)
                    else:
                        p.unlink()
                except Exception as e:
                    con.print(f"[red]{e}[/red]")

    def rename(self, args):
        if len(args) >= 2:
            paths = self.nums([args[0]])
            if paths:
                try:
                    paths[0].rename(self.cwd / args[1])
                except Exception as e:
                    con.print(f"[red]{e}[/red]")

    def touch(self, args):
        for name in args:
            (self.cwd / name).touch()

    def mkdir(self, args):
        for name in args:
            (self.cwd / name).mkdir(exist_ok=True)

    def search(self):
        result = subprocess.run(["search"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            con.print(f"[bold]{result.stdout.strip()}[/bold]")
        con.print("[dim]·[/dim]")
        input()

    def help(self, cmds):
        con.print(" ".join(f"[bold]{k}[/bold]" for k in cmds if len(k) == 1))
        input()


if __name__ == "__main__":
    FM(sys.argv[1] if len(sys.argv) > 1 else ".").run()
