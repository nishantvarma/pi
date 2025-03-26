#!/usr/bin/env python

import tkinter as tk


class EditorWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.tag = tk.Text(self, height=1, bg="#ffffea", bd=1, relief="flat", highlightthickness=0)
        self.tag.pack(fill=tk.X)
        self.editor = tk.Text(self, bd=0, relief="flat", highlightthickness=0)
        self.editor.pack(fill=tk.BOTH, expand=True)


class MainLayout(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.top = tk.Text(self, height=1, bg="#d3d3d3", bd=0, relief="flat", highlightthickness=0)
        self.top.pack(fill=tk.X)
        self.body = tk.Frame(self)
        self.body.pack(fill=tk.BOTH, expand=True)
        self.bottom = tk.Text(self, height=1, bg="#d3d3d3", bd=0, relief="flat", highlightthickness=0)
        self.bottom.config(state="disabled")
        self.bottom.pack(fill=tk.X)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Editor")
    root.option_add("*Font", ("DejaVu Sans Mono", 11))
    layout = MainLayout(root)
    layout.top.insert("1.0", "/home/nishant/src/pi/pi.py | Del Cut Paste Snarf Look Undo ")
    layout.bottom.config(state="normal")
    layout.bottom.insert("1.0", "1,1  All")
    layout.bottom.config(state="disabled")
    window = EditorWindow(layout.body)
    window.tag.insert("1.0", "/home/nishant/src/pi/pi.py | Del Cut Paste Snarf Look Undo ")
    window.editor.insert("1.0", "Hello, World.\n\nThanks for using Pi. Have a good day!\n")
    root.mainloop()
