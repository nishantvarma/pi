#!/usr/bin/python3.11

import tkinter as tk

from PIL import Image, ImageTk
from tkinter import ttk


class IconListView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("List View with Icons")
        self.tree = ttk.Treeview(self, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.folder_icon = ImageTk.PhotoImage(Image.open("folder_icon.png").resize((16, 16)))
        self.file_icon = ImageTk.PhotoImage(Image.open("file_icon.png").resize((16, 16)))
        self.insert_item("", "Folder 1", self.folder_icon)
        self.insert_item("", "File 1.txt", self.file_icon)
        self.insert_item("", "File 2.txt", self.file_icon)
        self.insert_item("", "Folder 2", self.folder_icon)

    def insert_item(self, parent, text, icon):
        self.tree.insert(parent, 'end', text=text, image=icon)


if __name__ == "__main__":
    app = IconListView()
    app.mainloop()