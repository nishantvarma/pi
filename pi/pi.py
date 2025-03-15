"""
Ability to respond to anything that comes in mind a.k.a shell.
Yank+
Current line should respect colors.
Delete should set index to next possible item.
New file should be auto-selected.
Make mouse selection same as keyboard selection.
Navigate back should highlight self.
Repeat previous find.
Allow resizing.
Improve guards.
Alt-Tab Switch (Queue)
Adapter Pattern
Seperation of Concern: Don't mix implementation with operations.
Switching to various implementations should be easy.
Modes
Code Duplication
Implement fuzzy open in new tab.
Auto-refresh files.
Recheck on subprocess cwd.
Console to shell etc.
Right click on output should repeat the command.
Tree + Icons?
Vis Integration
Scintilla?
Console could have a context.
https://thonny.org/
"""

import os
import shutil
import subprocess
import sys
import tkinter as tk
import traceback

from pathlib import Path
from tkinter import filedialog, Listbox, Menu, messagebox, simpledialog, ttk

from pi.config import config
from pi.core import exec_with_return, Folder


def restart(event=None):
    if messagebox.askyesno("Restart", "Are you sure?"):
        python = sys.executable
        os.execl(python, python, "-m", "pi.pi")


def quit(event=None):
    if messagebox.askyesno("Quit", "Are you sure?"):
        sys.exit(0)


class Console:
    def __init__(self, parent, prompt):
        self.buffer = str()
        self.prompt = prompt
        self.frame = ttk.Frame(parent)
        self.output = tk.Text(self.frame, state=tk.DISABLED, height=10)
        self.output.pack(fill=tk.BOTH, padx=4, pady=(4, 0))
        self.input = tk.Entry(self.frame)
        self.input.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(4, 0), pady=4)
        self.input.bind("<Control-l>", self.clear)
        self.frame.bind("<Enter>", lambda event: self.input.focus_set())
        self.input.bind("<Return>", self.execute)
        self.button = ttk.Button(self.frame, text="Restart", command=restart)
        self.button.pack(side=tk.RIGHT, padx=4)
        self.button = ttk.Button(self.frame, text="Clear", command=self.clear)
        self.button.pack(side=tk.RIGHT, padx=4)
        self.apply_theme()
        self.locals = {}

    def apply_theme(self):
        self.output.config(
            bg=config.console.output_bg,
            inactiveselectbackground=config.console.output_select_bg
        )
        self.input.config(
            bg=config.console.input_bg,
            selectbackground=config.console.input_select_bg
        )

    def write(self, message):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, message)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def execute(self, event=None):
        command = self.input.get().strip()
        self.input.delete(0, tk.END)
        if command:
            self.write(self.prompt + command + "\n")
            result = exec_with_return(command, globals(), self.locals)
            if result is not None:
                self.write(str(result) + "\n")

    def clear(self, event=None):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    def readline(self, prompt="Value"):
        return simpledialog.askstring("Input", prompt)


class Tabs(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.enable_traversal()
        self.master = master
        self.dragged = None
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-2>", self.close)
        self.bind("<Button-3>", self.master.duplicate_tab)

    def on_press(self, event):
        try:
            self.dragged = self.index(f"@{event.x},{event.y}")
        except:
            pass

    def on_release(self, event):
        if not hasattr(self, "dragged"):
            return
        source = self.dragged
        del self.dragged
        try:
            target = self.index(f"@{event.x},{event.y}")
        except:
            return
        if target != source:
            self.insert(target, self.tabs()[source])
        self.master.tab_activated()

    def close(self, event=None):
        if event:
            tab = self.tabs()[self.index(f"@{event.x},{event.y}")]
        else:
            tab = self.select()
        if len(self.tabs()) > 1:
            self.forget(tab)
            self.master.data.pop(tab)
            self.master.tab_activated()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.show_hidden = False
        self.title(config.app.title)
        self.geometry(config.app.geometry)
        self.configure(bg=config.app.bg)
        self.option_add("*Font", (config.app.font))
        self.heading = tk.Label(self, text="Pi")
        self.heading.pack(fill=tk.X)
        frame = ttk.Frame()
        frame.pack(fill=tk.X)
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, padx=4, expand=True)
        browse = tk.Button(frame, text="Browse", command=self.browse_folder)
        browse.pack(side=tk.LEFT, padx=(0, 4))
        refresh = tk.Button(frame, text="⟳", command = self.refresh_files)
        refresh.pack(side=tk.LEFT, padx=(0, 4))
        frame.bind("<Enter>", lambda event: entry.focus_set())
        self.tabs = Tabs(self)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        self.new_tab(os.getcwd())
        self.menu = Menu(self, tearoff=0)
        self.create_console()
        # self.embed()

    def load_files(self, box, dir, pattern=None):
        box.delete(0, tk.END)
        box.insert(tk.END, "..")
        folder = Folder(dir)
        for file in folder.get_files(self.show_hidden, pattern):
            box.insert(tk.END, file)
            attr = f"{folder.get_file_type(file)}_fg"
            box.itemconfig(tk.END, {"fg": getattr(config.explorer, attr)})
        box.selection_set(0)
        box.activate(0)
        box.focus_set()

    def new_tab(self, path):
        self.heading.config(text=path)
        frame = ttk.Frame(self.tabs)
        tab = str(frame)
        try:
            index = self.tabs.index(self.tabs.select()) + 1
        except:
            index = self.tabs.index("end")
        self.tabs.add(frame, text=os.path.basename(path) or path)
        self.tabs.insert(index, frame, text=os.path.basename(path) or path)
        self.tabs.select(frame)
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
        box.bind("<Button-3>", self.show_menu)
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
        box.bind("s", self.open_terminal)
        box.bind("x", self.fuzzy_open)
        box.bind("z", self.fuzzy_edit)
        self.load_files(box, path)
        return tab

    def duplicate_tab(self, event=None):
        source = self.tabs.select()
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
            tab = self.tabs.select()
            box = self.data[tab]["box"]
            dir = self.data[tab]["dir"]
            self.heading.config(text=dir)
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
        self.tabs.close()

    def create_console(self):
        if hasattr(self, "console"):
            return
        console = self.console = Console(self, prompt="> ")
        console.frame.pack(side=tk.BOTTOM, fill=tk.X)
        frame = ttk.Frame(self)
        sys.stdin, sys.stdout, sys.stderr = console, console, console

    def check_process(self):
        if self.process.poll() is not None:
            print("Terminal exited. Removing embedded frame.")
            self.win.destroy()
        else:
            self.after(500, self.check_process)

    def embed(self):
        self.win = tk.Frame(self, width=600, height=400, bg="black")
        self.win.pack(fill=tk.BOTH, expand=True)
        winid = str(self.win.winfo_id())
        self.process = subprocess.Popen(["st", "-w", winid])
        self.win.focus_set()
        self.check_process()

    def box_context(self):
        tab = self.tabs.select()
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
        self.heading.config(text=path)
        self.data[tab]["dir"] = path
        self.load_files(box, path)
        self.tabs.tab(tab, text=os.path.basename(path) or path)

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
        if os.path.isdir(path):
            self.change_folder(tab, box, path)
        else:
            subprocess.run(["edit", path], cwd=dir)

    def filter_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        pattern = simpledialog.askstring("Filter", "Pattern:")
        self.load_files(box, dir, pattern=pattern)

    def fuzzy_edit(self, event=None):
        tab, box, dir, paths = self.box_context()
        subprocess.run(["spawn", "st", "fuzzyedit", dir])

    def fuzzy_open(self, event=None):
        tab, box, dir, paths = self.box_context()
        subprocess.run(["spawn", "st", "fuzzyopen", dir])

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
        if os.path.isdir(path):
            self.change_folder(tab, box, path)
        else:
            subprocess.run(["open", path], cwd=dir)

    def open_parent(self, event=None):
        tab, box, dir, path = self.box_context()
        parent = os.path.dirname(dir)
        if parent and parent != dir:
            self.heading.config(text=parent)
            self.data[tab]["dir"] = parent
            self.load_files(self.data[tab]["box"], parent)
            self.tabs.tab(tab, text=os.path.basename(parent) or parent)

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
            subprocess.run(["spawn", program, path], cwd=dir)

    def paste_files(self, event=None):
        tab, box, dir, paths = self.box_context()
        if not hasattr(self, "copied_files"):
            return
        for path in self.copied_files:
            name = os.path.basename(path)
            dest = os.path.join(dir, name)
            if os.path.exists(dest):
                print(f"Desination {dest} exists")
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

    def show_menu(self, event):
        tab, box, dir, paths = self.box_context()
        selection = box.curselection()
        if len(selection) <= 1:
            box.selection_clear(0, tk.END)
            nearest = box.nearest(event.y)
            box.select_set(nearest)
            box.activate(nearest)
            path = os.path.join(dir, box.get(nearest))
        else:
            path = dir
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


if __name__ == "__main__":
    a = App()
    a.bind_all("<Control-q>", quit)
    a.bind_all("<Control-r>", restart)
    a.bind_all("<F11>", a.toggle_fullscreen)
    a.geometry("{}x{}+0+0".format(*a.maxsize()))
    a.mainloop()
