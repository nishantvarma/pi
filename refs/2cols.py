#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Multi-Column List")
tree = ttk.Treeview(root, columns=("Column 1", "Column 2"), show="headings")
tree.heading("Column 1", text="Name")
tree.heading("Column 2", text="Age")
data = [("Alice", 25), ("Bob", 30), ("Charlie", 22)]
for item in data:
    tree.insert(str(), tk.END, values=item)
tree.pack(fill=tk.BOTH, expand=True)

root.mainloop()
