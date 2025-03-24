#!/usr/bin/env python

import os
import tkinter as tk

from pathlib import Path
from tkinter import ttk


class FileExplorer(tk.Frame):
    def __init__(self, parent, *args, path=None, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack_propagate(False)
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree_x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_y_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(self.tree_frame, show="tree")
        self.tree.config(yscrollcommand=self.tree_y_scroll.set)
        self.tree.config(xscrollcommand=self.tree_x_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree_y_scroll.config(command=self.tree.yview)
        self.tree_x_scroll.config(command=self.tree.xview)
        self.tree.column("#0", minwidth=150, width=300, stretch=True)
        self.tree.bind("<Left>", self.natural_left)
        self.tree.bind("<Right>", self.natural_right)
        self.tree.bind("<Button-3>", self.mouse_expand_collapse)
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill=tk.X)
        self.toggle_all_button = tk.Button(self.search_frame, text="⯈", command=self.expand_selected_recursive)
        self.toggle_all_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.refresh_button = tk.Button(self.search_frame, text="Refresh", command=self.refresh_tree)
        self.refresh_button.pack(side=tk.RIGHT, padx=5, pady=5)
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

    def expand_selected(self, event):
        selected = self.tree.selection()
        if selected:
            for node in selected:
                self.tree.item(node, open=True)
                self.expand_one_level(node)

    def collapse_selected(self, event):
        selected = self.tree.selection()
        if selected:
            for node in selected:
                self.tree.item(node, open=False)

    def toggle_selected(self, event):
        selected = self.tree.selection()
        if selected:
            for node in selected:
                self.toggle_node(node)

    def toggle_all(self):
        for item in self.tree.get_children():
            self.toggle_node(item)

    def toggle_current(self):
        selected = self.tree.selection()
        if selected:
            for node in selected:
                self.toggle_node(node)

    def toggle_node(self, item):
        current_state = self.tree.item(item, "open")
        self.tree.item(item, open=not current_state)
        if not current_state:
            self.expand_one_level(item)

    def search_tree(self):
        query = self.search_var.get().lower()
        if not query:
            return
        queue = [(item, 0) for item in self.tree.get_children()]
        self.search_results = []
        while queue:
            item, depth = queue.pop(0)
            if depth > 6:
                continue
            if query in self.tree.item(item, "text").lower():
                self.search_results.append(item)
            children = self.tree.get_children(item)
            if children:
                queue.extend((child, depth + 1) for child in children)
        self.search_index = 0
        self.highlight_search_result()

    def highlight_search_result(self):
        if self.search_results:
            item = self.search_results[self.search_index]
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.tree.see(item)

    def search_next(self):
        if self.search_results:
            self.search_index = (self.search_index + 1) % len(self.search_results)
            self.highlight_search_result()

    def search_prev(self):
        if self.search_results:
            self.search_index = (self.search_index - 1) % len(self.search_results)
            self.highlight_search_result()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Explorer")
    root.geometry("600x600")
    explorer = FileExplorer(root)
    explorer.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
