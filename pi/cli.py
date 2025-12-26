#!/usr/bin/env python3

import glob
import os
import readline
import shutil
import subprocess
import sys
from pathlib import Path

from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

con = Console()


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
        self.init_readline()

    def init_readline(self):
        readline.set_completer(self.complete)
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")

    def complete(self, text, state):
        matches = glob.glob(os.path.expanduser(text) + "*")
        return (matches + [None])[state]

    def style(self, p):
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
            style, suf = self.style(f)
            mark = "* " if f in self.sel else "  "
            t.add_row(str(i), f"{mark}[{style}]{f.name}{suf}[/{style}]")
        if len(self.files) > h:
            t.add_row("", f"[dim]+{len(self.files) - h} more[/dim]")

        try:
            path = "~/" + str(self.cwd.relative_to(Path.home()))
        except ValueError:
            path = str(self.cwd)
        title = f"[bold]{path}[/bold]"
        if self.sel:
            title += f" [dim]sel:{len(self.sel)}[/dim]"
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
            "..": "up",
            "b": "up",
            "~": "home",
            "h": "hidden",
            "e": "edit",
            "o": "open",
            "c": "copy",
            "x": "cut",
            "v": "paste",
            "d": "delete",
            "r": "rename",
            "n": "touch",
            "m": "mkdir",
            "l": "list",
            "g": "mark",
            "s": "select",
            "ss": "unselect",
            "q": "quit",
            "?": "help",
        }
        actions = {
            "up": lambda: self.go_up(),
            "home": lambda: self.go_home(),
            "hidden": lambda: self.toggle_hidden(),
            "edit": lambda: self.edit(args),
            "open": lambda: self.open(args),
            "copy": lambda: self.yank(args),
            "cut": lambda: self.yank(args, cut=True),
            "paste": lambda: self.paste(),
            "delete": lambda: self.delete(args),
            "rename": lambda: self.rename(args),
            "touch": lambda: self.touch(args),
            "mkdir": lambda: self.mkdir(args),
            "list": lambda: self.ls(),
            "mark": lambda: self.go_mark(args),
            "select": lambda: self.select(args),
            "unselect": lambda: self.sel.clear(),
            "quit": lambda: sys.exit(0),
            "help": lambda: self.help(cmds),
        }
        while True:
            self.draw()
            try:
                line = input("; ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                self.cd(self.prev)
                self.ls()
                continue

            if line.isdigit():
                self.go(int(line))
                self.ls()
                continue

            if line.startswith("!"):
                r = subprocess.run(line[1:], shell=True)
                con.print("[green]·[/green]" if r.returncode == 0 else "[red]·[/red]")
                input()
                self.ls()
                continue

            parts = line.split()
            cmd, args = parts[0], parts[1:]

            if cmd in cmds:
                actions[cmds[cmd]]()
                self.ls()
                continue

            if self.go_name(cmd):
                self.ls()
                continue

            r = subprocess.run(line, shell=True)
            con.print("[green]·[/green]" if r.returncode == 0 else "[red]·[/red]")
            input()
            self.ls()

    def cd(self, p):
        if p != self.cwd:
            self.prev = self.cwd
        self.cwd = p
        os.chdir(p)
        self.sel.clear()

    def go_up(self):
        if self.cwd.parent != self.cwd:
            self.cd(self.cwd.parent)

    def go_home(self):
        self.cd(Path.home())

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
                self.cd(p)
            else:
                subprocess.run(["open", str(p)])

    def select(self, args):
        if not args:
            for p in self.sel:
                con.print(f"[bold]{p.name}[/bold]")
            if self.sel:
                input()
            return
        for p in self.nums(args):
            if p in self.sel:
                self.sel.remove(p)
            else:
                self.sel.add(p)

    def yank(self, args, cut=False):
        self.clip = self.nums(args) if args else list(self.sel)
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
                con.print(f"[red]{e}[/red]")
        if self.cut:
            self.clip = []

    def delete(self, args):
        paths = self.nums(args) if args else list(self.sel)
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
        items = [f"[bold]{k}[/bold]:{v}" for k, v in cmds.items()]
        con.print(Columns(items, equal=True, expand=True))
        input()


if __name__ == "__main__":
    FM(sys.argv[1] if len(sys.argv) > 1 else ".").run()
