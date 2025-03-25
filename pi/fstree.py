#!/usr/bin/env python

import os
import tkinter as tk

from pathlib import Path
from tkinter import ttk


class FSTree(tk.Frame):
    def __init__(self, parent, *args, path=None, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack_propagate(False)
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.x_scroll = ttk.Scrollbar(self.frame, orient="horizontal")
        self.x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.y_scroll = ttk.Scrollbar(self.frame, orient="vertical")
        self.y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(self.frame, show="tree")
        self.tree.config(yscrollcommand=self.y_scroll.set)
        self.tree.config(xscrollcommand=self.x_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.y_scroll.config(command=self.tree.yview)
        self.x_scroll.config(command=self.tree.xview)
        self.tree.column("#0", minwidth=150, width=300, stretch=True)
        self.tree.bind("<Left>", self.natural_left)
        self.tree.bind("<Right>", self.natural_right)
        self.tree.bind("<Button-3>", self.toggle_fold)
        self.populate_tree(path=path)

    def populate_tree(self, path=Path.home(), parent=""):
        if not path:
            path = Path.home()
        try:
            for entry in sorted(path.iterdir()):
                is_dir = entry.is_dir()
                node = self.tree.insert(parent, "end", text=entry.name, open=False, values=[str(entry)])
                if is_dir:
                    self.tree.insert(node, "end", text="...")
            first_node = self.tree.get_children(parent)[:1]
            if first_node:
                first_node = first_node[0]
                self.tree.selection_set(first_node)
                self.tree.focus(first_node)
                self.tree.see(first_node)
        except PermissionError:
            pass

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.populate_tree()

    def expand_one_level(self, item):
        children = self.tree.get_children(item)
        if children and self.tree.item(children[0], "text") == "...":
            self.tree.delete(children[0])
            path = Path(self.tree.item(item, "values")[0])
            try:
                for entry in sorted(path.iterdir()):
                    is_dir = entry.is_dir()
                    node = self.tree.insert(item, "end", text=entry.name, open=False, values=[str(entry)])
                    if is_dir:
                        self.tree.insert(node, "end", text="...")
            except PermissionError:
                pass

    def expand_multi_level(self, max_level=3):
        def expand_recursive(node, level):
            if level >= max_level:
                return
            self.expand_one_level(node)
            for child in self.tree.get_children(node):
                expand_recursive(child, level + 1)
        selected = self.tree.selection()
        for node in selected:
            expand_multi_level(node, 0)

    def natural_left(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        current = selected[0]
        if not self.tree.item(current, "open"):
            self.tree.event_generate("<Up>")
            return "break"

    def natural_right(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        current = selected[0]
        if not self.tree.get_children(current) or self.tree.item(current, "open"):
            self.tree.event_generate("<Down>")
            return "break"

    def toggle_fold(self, event):
        selected = self.tree.selection()
        if selected:
            for node in selected:
                if self.tree.item(node, "open"):
                    self.tree.item(node, open=False)
                else:
                    self.tree.item(node, open=True)
                    self.expand_one_level(node)


if __name__ == "__main__":
    import shutil
    try:
        Path("tree/folder/folder").mkdir(parents=True, exist_ok=True)
        for file in ["tree/file", "tree/folder/file", "tree/folder/folder/file"]:
            Path(file).touch()
        root = tk.Tk()
        root.title("File System Tree")
        root.geometry("800x600")
        explorer = FSTree(root, path=Path("tree"))
        explorer.pack(fill=tk.BOTH, expand=True)
        root.mainloop()
    finally:
        shutil.rmtree("tree", ignore_errors=True)
