import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk

from pathlib import Path
from tkinter import filedialog, Listbox, Menu, messagebox, simpledialog, ttk

from pi import history, server
from pi.config import config
from pi.console import Console
from pi.core import Folder
from pi import help
from pi.tab import Tab
from pi.tray import Tray
from pi.utils import quit, restart


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.show_hidden = False
        self.bindings = [
            ("↑/↓", "Move", None),
            ("←/→", "Parent / Open", None),
            ("Return", "Open", None),
            ("!", "Filter", self.filter_files),
            ("*", "Executable", self.make_executable),
            ("/", "Search", self.search_file),
            ("`", "Dup tab", self.duplicate_tab),
            ("e", "Edit", self.edit_file),
            ("b", "Buffer", self.search_buffer),
            ("h", "Help", self.show_help),
            ("l", "Link", self.create_links),
            ("n", "New file", self.create_file),
            ("o", "New folder", self.create_folder),
            ("q", "Close/Quit", self.close_tab),
            ("Q", "Force quit", None),
            ("s", "Terminal", self.open_terminal),
            ("x", "Fuzzy open", self.fuzzy_open),
            ("z", "Fuzzy edit", self.fuzzy_edit),
            ("Z", "Fuzzy home", self.fuzzy_home),
            ("Del", "Delete", None),
            ("F2", "Rename", None),
            ("F5", "Refresh", None),
            ("Ctrl+c/x/v", "Copy/Cut/Paste", None),
        ]
        self.title(config.app.title)
        self.geometry(config.app.geometry)
        self.configure(bg=config.app.bg)
        self.option_add("*Font", config.app.font)
        self.tab = Tab(self)
        self.tab.pack(fill=tk.BOTH, expand=True)
        self.menu = Menu(self, tearoff=0)
        # self.create_console()
        self.new_tab(os.getcwd())

    def load_files(self, box, dir, pattern=None, selection=None):
        box.delete(0, tk.END)
        box.insert(tk.END, "..")
        folder = Folder(dir)
        position = 0
        for index, file in enumerate(folder.get_files(self.show_hidden, pattern)):
            box.insert(tk.END, file)
            attr = f"{folder.get_file_type(file)}_fg"
            box.itemconfig(tk.END, {"fg": getattr(config.explorer, attr)})
            if selection and file == selection:
                position = index
        box.selection_set(position + 1)
        box.activate(position + 1)
        box.focus_set()

    def new_tab(self, path):
        history.add(path)
        frame = ttk.Frame(self.tab)
        tab = str(frame)
        try:
            index = self.tab.index(self.tab.select()) + 1
        except:
            index = self.tab.index("end")
        self.tab.add(frame, text=os.path.basename(path) or path)
        self.tab.insert(index, frame, text=os.path.basename(path) or path)
        self.tab.select(frame)
        box = Listbox(frame, selectmode="extended", activestyle="none")
        box.config(bg=config.explorer.bg, selectbackground=config.explorer.select_bg)
        box.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        scrollbar = tk.Scrollbar(box, orient=tk.VERTICAL)
        scrollbar.config(command=box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        box.config(yscrollcommand=scrollbar.set)
        self.data[tab] = {"dir": path, "frame": frame, "box": box}
        box.bind("!", self.filter_files)
        box.bind("*", self.make_executable)
        box.bind("/", self.search_file)
        box.bind("<Button-1>", self.hide_menu)
        box.bind("<Button-2>", self.duplicate_tab)
        box.bind("<ButtonPress-3>", self.on_press)
        box.bind("<ButtonRelease-3>", self.on_release)
        box.bind("<Control-c>", self.copy_files)
        box.bind("<Control-o>", self.browse_folder)
        box.bind("<Control-v>", self.paste_files)
        box.bind("<Control-x>", self.cut_files)
        box.bind("<Delete>", self.delete_files)
        box.bind("<Double-1>", self.open_file)
        box.bind("<Enter>", lambda event: self.tab_activated())
        box.bind("<Escape>", self.hide_menu)
        box.bind("<F2>", self.rename_file)
        box.bind("<F5>", self.refresh_files)
        box.bind("<Left>", self.open_parent)
        box.bind("<Motion>", self.highlight_current_line)
        box.bind("<Return>", self.open_file)
        box.bind("<Right>", self.open_file)
        box.bind("`", self.duplicate_tab)
        box.bind("e", self.edit_file)
        box.bind("l", self.create_links)
        box.bind("n", self.create_file)
        box.bind("o", self.create_folder)
        box.bind("q", self.close_tab)
        box.bind("Q", lambda e: sys.exit(0))
        box.bind("s", self.open_terminal)
        box.bind("x", self.fuzzy_open)
        box.bind("z", self.fuzzy_edit)
        box.bind("b", self.search_buffer)
        box.bind("h", self.show_help)
        box.bind("Z", self.fuzzy_home)
        self.load_files(box, path)
        return tab

    def duplicate_tab(self, event=None):
        source = self.tab.select()
        if source:
            target = self.new_tab(self.data[source]["dir"])
            source = self.data[source]["box"]
            target = self.data[target]["box"]
            target.selection_clear(0, "end")
            focused = source.index(tk.ACTIVE)
            target.selection_set(focused)
            target.activate(focused)
            target.see(focused)
            target.focus_set()

    def tab_activated(self):
        try:
            tab = self.tab.select()
            box = self.data[tab]["box"]
            dir = self.data[tab]["dir"]
            if box.size() == 0:
                return
            focused = box.index(tk.ACTIVE)
            selection = box.curselection()
            if not selection:
                box.selection_set(focused)
            box.focus_set()
        except:
            pass

    def close_tab(self, event=None):
        if len(self.tab.tabs()) == 1:
            quit()
        else:
            self.tab.close()

    def create_console(self):
        if hasattr(self, "console"):
            return
        console = self.console = Console(self, prompt="> ")
        console.frame.pack(fill=tk.X)
        frame = ttk.Frame(self)
        sys.stdin, sys.stdout, sys.stderr = console, console, console

    def box_context(self):
        tab = self.tab.select()
        box = self.data[tab]["box"]
        dir = self.data[tab]["dir"]
        selection = box.curselection()
        if not selection:
            return tab, box, dir, None
        items = [box.get(i) for i in selection]
        paths = [
            os.path.join(dir, item) if item != ".." else os.path.dirname(dir)
            for item in items
        ]
        return tab, box, dir, paths

    def highlight_current_line(self, event):
        return
        tab, box, dir, paths = self.box_context()
        index = box.nearest(event.y)
        box.itemconfig(index, {"bg": "lightgray", "fg": "black"})

    def browse_folder(self, event=None):
        dir = filedialog.askdirectory()
        if dir:
            self.new_tab(dir)

    def copy_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        self.paste_mode = "copy"
        self.copied_files = paths
        if not paths:
            return
        names = [os.path.basename(path) for path in paths]
        print(f"Copied {', '.join(names)} from {dir}")

    def change_folder(self, tab, box, path):
        self.data[tab]["dir"] = path
        self.load_files(box, path)
        self.tab.tab(tab, text=os.path.basename(path) or path)

    def create_file(self, event=None):
        tab, box, dir, paths = self.box_context()
        name = simpledialog.askstring("New File", "File name:")
        if name:
            Path.touch(os.path.join(dir, name))
            self.load_files(box, dir)

    def create_folder(self, event=None):
        tab, box, dir, paths = self.box_context()
        name = simpledialog.askstring("New Folder", "Folder name:")
        if name:
            os.mkdir(os.path.join(dir, name))
            self.load_files(box, dir)

    def create_links(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not hasattr(self, "copied_files"):
            return
        for file in self.copied_files:
            link = os.path.relpath(file, dir)
            os.symlink(link, os.path.join(dir, os.path.basename(link)))
            print(f"Linked as {link} to {dir}")
        self.load_files(box, dir)

    def cut_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        self.paste_mode = "cut"
        self.copied_files = paths
        if not paths:
            return
        names = [os.path.basename(path) for path in paths]
        print(f"Cut {', '.join(names)} from {dir}")

    def delete_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not paths:
            return
        names = [os.path.basename(path) for path in paths]
        print(f"Files to be deleted {', '.join(names)} from {dir}")
        if messagebox.askyesno("Confirm", "Are you sure?"):
            for path in paths:
                if os.path.islink(path):
                    os.remove(path)
                elif os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    os.rmdir(path)
            self.load_files(box, dir)

    def edit_file(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not paths:
            return
        path = paths[0]
        history.add(path)
        if os.path.isdir(path):
            self.change_folder(tab, box, path)
        else:
            subprocess.run(["edit", path], cwd=os.path.dirname(path))

    def filter_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        pattern = simpledialog.askstring("Filter", "Pattern:")
        self.load_files(box, dir, pattern=pattern)

    def fuzzy_edit(self, event=None):
        tab, box, dir, paths = self.box_context()
        subprocess.run(["spawn", "st", "fuzzyedit"], cwd=dir)

    def fuzzy_home(self, event=None):
        home = os.path.expanduser("~")
        fd, resultfile = tempfile.mkstemp()
        os.close(fd)
        subprocess.run([
            "st", "-e", "sh", "-c",
            f"find {home} -maxdepth 3 -type d 2>/dev/null | fzy > {resultfile}"
        ])
        try:
            path = open(resultfile).read().strip()
        finally:
            os.unlink(resultfile)
        if path and os.path.isdir(path):
            for tab_id, data in self.data.items():
                if data["dir"] == path:
                    history.add(path)
                    self.tab.select(tab_id)
                    return
            self.new_tab(path)

    def fuzzy_open(self, event=None):
        tab, box, dir, paths = self.box_context()
        subprocess.run(["spawn", "st", "fuzzyopen"], cwd=dir)

    def make_executable(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not paths:
            return
        path = paths[0]
        os.chmod(path, 0o755)
        focused = box.index(tk.ACTIVE)
        box.itemconfig(focused, {"fg": config.explorer.executable_fg})

    def open_file(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not paths:
            return
        path = paths[0]
        history.add(path)
        if os.path.isdir(path):
            self.change_folder(tab, box, path)
        else:
            subprocess.run(["open", path], cwd=os.path.dirname(path))

    def open_parent(self, event=None):
        tab, box, dir, path = self.box_context()
        parent = os.path.dirname(dir)
        name = os.path.basename(dir)
        if parent and parent != dir:
            history.add(parent)
            self.data[tab]["dir"] = parent
            self.load_files(self.data[tab]["box"], parent, selection=name)
            self.tab.tab(tab, text=os.path.basename(parent) or parent)

    def open_terminal(self, event=None):
        tab, box, dir, paths = self.box_context()
        subprocess.run(["spawn", "st"], cwd=dir)

    def open_with(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not paths:
            return
        path = paths[0]
        program = simpledialog.askstring("Open", "Program:")
        if program:
            history.add(path)
            subprocess.run(["spawn", program, path], cwd=dir)

    def paste_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not hasattr(self, "copied_files"):
            return
        for path in self.copied_files:
            name = os.path.basename(path)
            dest = os.path.join(dir, name)
            if os.path.exists(dest):
                print(f"Destination {dest} exists")
                if name := filedialog.asksaveasfilename(initialdir=dir, initialfile=name):
                    dest = os.path.join(dir, name)
                else:
                    print(f"Skipping {path}")
                    continue
            if self.paste_mode == "copy":
                print(path, dest)
                shutil.copy(path, dest, follow_symlinks=False)
            elif self.paste_mode == "cut":
                shutil.move(path, dest)
            print(f"Pasted {path} to {dir} as {name}")
        if self.paste_mode == "cut":
            self.copied_files = []
        self.load_files(box, dir)

    def rename_file(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not paths:
            return
        path = paths[0]
        name = os.path.basename(path)
        name = simpledialog.askstring("Rename", f"Rename {path} to:", initialvalue=name)
        if name:
            os.rename(path, os.path.join(dir, name))
            self.load_files(box, dir)

    def refresh_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        if tab:
            self.load_files(box, dir)

    def search_file(self, event=None):
        tab, box, dir, paths = self.box_context()
        pattern = simpledialog.askstring("Search", "Pattern:")
        if not pattern:
            return
        focused = box.index(tk.ACTIVE)
        if focused is None:
            focused = -1
        start = (focused + 1) % box.size()
        for i in range(box.size()):
            index = (start + i) % box.size()
            text = box.get(index).lower()
            if pattern.lower() in text:
                box.selection_clear(0, tk.END)
                box.selection_set(index)
                box.activate(index)
                box.see(index)
                return

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def toggle_hidden(self, event=None):
        tab, box, dir, paths = self.box_context()
        self.show_hidden = not self.show_hidden
        self.load_files(box, dir)

    def select_file(self, box, name):
        for i in range(box.size()):
            if box.get(i) == name:
                box.selection_clear(0, tk.END)
                box.selection_set(i)
                box.activate(i)
                box.see(i)
                return True
        return False

    def search_buffer(self, event=None):
        active = [data["dir"] for data in self.data.values()]
        items = active + [p for p in history.get_all() if p not in active]
        if not items:
            return
        fd, histfile = tempfile.mkstemp()
        os.write(fd, "\n".join(items).encode())
        os.close(fd)
        fd, resultfile = tempfile.mkstemp()
        os.close(fd)
        subprocess.run([
            "st", "-e", "sh", "-c",
            f"fzy < {histfile} > {resultfile}"
        ])
        try:
            path = open(resultfile).read().strip()
        finally:
            os.unlink(histfile)
            os.unlink(resultfile)
        if not path:
            return
        for tab_id, data in self.data.items():
            if data["dir"] == path:
                self.tab.select(tab_id)
                return
            if os.path.dirname(path) == data["dir"]:
                self.tab.select(tab_id)
                self.select_file(data["box"], os.path.basename(path))
                subprocess.run(["open", path], cwd=os.path.dirname(path))
                return
        if os.path.isdir(path):
            self.new_tab(path)
        elif os.path.exists(path):
            parent = os.path.dirname(path)
            self.new_tab(parent)
            tab = self.tab.select()
            self.select_file(self.data[tab]["box"], os.path.basename(path))
            subprocess.run(["open", path], cwd=os.path.dirname(path))

    def show_help(self, event=None):
        help.toggle(self, self.bindings)

    def on_press(self, event):
        self.press_start_time = event.time

    def on_release(self, event):
        press_duration = event.time - self.press_start_time
        tab, box, dir, paths = self.box_context()
        selection = box.curselection()
        if len(selection) <= 1:
            box.selection_clear(0, tk.END)
            nearest = box.nearest(event.y)
            box.select_set(nearest)
            box.activate(nearest)
            name = box.get(nearest)
            if name == "..":
                path = os.path.dirname(dir)
            else:
                path = os.path.join(dir, box.get(nearest))
        else:
            path = dir
        if press_duration >= 175:
            self.show_menu(event, path)
        else:
            if os.path.isdir(path):
                self.new_tab(path)
            else:
                self.open_file(event)

    def show_menu(self, event, path):
        self.menu.delete(0, tk.END)
        self.menu.add_command(label="Open", command=self.open_file)
        self.menu.add_command(label="Open With", command=self.open_with)
        if os.path.isdir(path):
            self.menu.add_command(label="Open in New Tab", command=lambda: self.new_tab(path))
        self.menu.add_separator()
        self.menu.add_command(label="Edit", command=self.edit_file)
        self.menu.add_command(label="Rename", command=self.rename_file)
        self.menu.add_separator()
        self.menu.add_command(label="Copy", command=self.copy_files)
        self.menu.add_command(label="Cut", command=self.cut_files)
        self.menu.add_command(label="Paste", command=self.paste_files)
        self.menu.add_command(label="Link", command=self.create_links)
        self.menu.add_separator()
        self.menu.add_command(label="New File", command=self.create_file)
        self.menu.add_command(label="New Folder", command=self.create_folder)
        self.menu.add_command(label="Delete", command=self.delete_files)
        self.menu.add_separator()
        self.menu.add_command(label="Open Terminal", command=self.open_terminal)
        self.menu.add_command(label="Toggle Hidden", command=self.toggle_hidden)
        self.menu.post(event.x_root, event.y_root)

    def hide_menu(self, event):
        self.menu.unpost()


def open_path(app, path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return
    for tab_id, data in app.data.items():
        if data["dir"] == path:
            history.add(path)
            app.tab.select(tab_id)
            app.lift()
            app.focus_force()
            return
    if os.path.isdir(path):
        app.new_tab(path)
    else:
        subprocess.run(["open", path], cwd=os.path.dirname(path))
    app.lift()
    app.focus_force()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        path = os.path.abspath(os.path.expanduser(path))

    if server.is_running():
        if path:
            server.send(path)
        else:
            print("already running")
        sys.exit(0)

    a = App()
    server.start(lambda p: a.after(0, lambda: open_path(a, p)))

    style = ttk.Style()
    style.configure(".", font=config.app.font)
    a.bind_all("<Control-q>", quit)
    a.bind_all("<Control-r>", restart)
    a.bind_all("<F11>", a.toggle_fullscreen)
    a.mainloop()
