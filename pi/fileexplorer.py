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

    def expand_selected_recursive(self, max_depth=3):
        def expand_recursive(node, depth):
            if depth >= max_depth:
                return
            self.expand_one_level(node)
            for child in self.tree.get_children(node):
                expand_recursive(child, depth + 1)
        selected = self.tree.selection()
        for node in selected:
            expand_recursive(node, 0)

    def natural_right(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        current = selected[0]
        children = self.tree.get_children(current)
        if children:
            next_node = children[0]
        else:
            next_node = self.tree.next(current)
            parent = self.tree.parent(current)
            while not next_node and parent:
                next_node = self.tree.next(parent)
                parent = self.tree.parent(parent)
        if next_node:
            self.tree.selection_set(next_node)
            self.tree.focus(next_node)
            self.tree.see(next_node)
        return "break"

    def natural_left(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        current = selected[0]
        prev_node = self.tree.prev(current)
        if prev_node:
            while self.tree.get_children(prev_node):
                prev_node = self.tree.get_children(prev_node)[-1]
        else:
            prev_node = self.tree.parent(current)
        if prev_node:
            self.tree.selection_set(prev_node)
            self.tree.focus(prev_node)
            self.tree.see(prev_node)
        return "break"

    def natural_right(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        current = selected[0]
        if not self.tree.get_children(current) or self.tree.item(current, "open"):
            self.tree.event_generate("<Down>")
            return "break"

    def natural_left(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        current = selected[0]
        if not self.tree.item(current, "open"):
            self.tree.event_generate("<Up>")
            return "break"

    def get_next_node(self, node):
        children = self.tree.get_children(node)
        if children:
            return children[0]
        while node:
            sibling = self.tree.next(node)
            if sibling:
                return sibling
            node = self.tree.parent(node)
        return None

    def get_prev_node(self, node):
        prev_sibling = self.tree.prev(node)
        if prev_sibling:
            last_child = self.get_deepest_child(prev_sibling)
            return last_child if last_child else prev_sibling
        return self.tree.parent(node)

    def get_deepest_child(self, node):
        children = self.tree.get_children(node)
        while children:
            node = children[-1]
            children = self.tree.get_children(node)
        return node

    def mouse_expand_collapse(self, event):
        selected = self.tree.selection()
        if selected:
            for node in selected:
                if self.tree.item(node, "open"):
                    self.tree.item(node, open=False)
                else:
                    self.tree.item(node, open=True)
                    self.expand_one_level(node)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Explorer")
    root.geometry("600x600")
    explorer = FileExplorer(root)
    explorer.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
