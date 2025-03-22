#!/usr/bin/env python

import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path

class FileExplorer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Search bar frame
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.search_entry.bind("<Return>", lambda event: self.search_tree())  # Bind Enter key
        
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_tree)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.prev_button = tk.Button(self.search_frame, text="Prev", command=self.search_prev)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.next_button = tk.Button(self.search_frame, text="Next", command=self.search_next)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree_y_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(self.tree_frame, show='tree', 
                                 yscrollcommand=self.tree_y_scroll.set, 
                                 xscrollcommand=self.tree_x_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree_y_scroll.config(command=self.tree.yview)
        self.tree_x_scroll.config(command=self.tree.xview)
        
        self.tree.column("#0", width=300, stretch=False)  # Set initial width, prevent automatic stretching
        
        self.tree.bind("<<TreeviewOpen>>", self.on_expand)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Cantarell", 10))
        
        self.max_width = 300  # Track maximum width for horizontal scrolling
        self.search_results = []
        self.search_index = -1
        self.populate_tree()
    
    def populate_tree(self, path=Path.home(), parent=""):
        try:
            for entry in sorted(path.iterdir()):
                is_dir = entry.is_dir()
                node = self.tree.insert(parent, "end", text=entry.name, open=False, values=[str(entry)])
                
                if is_dir:
                    self.tree.insert(node, "end", text="...")  # Placeholder for lazy loading
                
                self.update_column_width(entry.name)  # Update column width dynamically
        except PermissionError:
            pass  # Skip folders without permission

    def on_expand(self, event):
        item_id = self.tree.focus()
        if item_id:
            self.expand_node(item_id)
    
    def expand_node(self, item_id):
        path = Path(self.tree.item(item_id, "values")[0])
        if path.is_dir():
            self.tree.delete(*self.tree.get_children(item_id))  # Remove placeholder
            self.populate_tree(path, item_id)
            self.adjust_scroll_region()
    
    def update_column_width(self, text):
        text_width = len(text) * 7  # Approximate character width
        if text_width > self.max_width:
            self.max_width = text_width
            self.tree.column("#0", width=self.max_width)
            self.adjust_scroll_region()
    
    def adjust_scroll_region(self):
        self.tree.update_idletasks()
        self.tree_x_scroll.config(command=self.tree.xview)
        self.tree_y_scroll.config(command=self.tree.yview)
    
    def on_double_click(self, event):
        item_id = self.tree.focus()
        if item_id:
            print("Selected:", self.tree.item(item_id, "text"))
    
    def search_tree(self):
        query = self.search_var.get().lower()
        if not query:
            return
        
        self.search_results = []
        for item in self.tree.get_children():
            self.search_node_bfs(item, query, max_depth=6)
        
        if self.search_results:
            self.search_index = 0
            self.focus_search_result()
    
    def search_node_bfs(self, root_item, query, max_depth):
        queue = [(root_item, 0)]  # (node, depth)
        
        while queue:
            item, depth = queue.pop(0)
            text = self.tree.item(item, "text").lower()
            
            if query in text:
                self.search_results.append(item)
            
            if depth < max_depth:
                children = self.tree.get_children(item)
                if "..." in [self.tree.item(child, "text") for child in children]:
                    self.expand_node(item)  # Expand if placeholder exists
                    children = self.tree.get_children(item)  # Get new children after expansion
                
                for child in children:
                    queue.append((child, depth + 1))
    
    def expand_to_item(self, item):
        parent = self.tree.parent(item)
        while parent:
            self.tree.item(parent, open=True)
            parent = self.tree.parent(parent)
    
    def focus_search_result(self):
        if 0 <= self.search_index < len(self.search_results):
            item = self.search_results[self.search_index]
            self.expand_to_item(item)
            self.tree.selection_set(item)
            self.tree.see(item)
    
    def search_next(self):
        if self.search_results:
            self.search_index = (self.search_index + 1) % len(self.search_results)
            self.focus_search_result()
    
    def search_prev(self):
        if self.search_results:
            self.search_index = (self.search_index - 1) % len(self.search_results)
            self.focus_search_result()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Explorer")
    root.geometry("400x600")
    
    explorer = FileExplorer(root)
    explorer.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
