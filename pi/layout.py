#!../.venv/bin/python

import tkinter as tk

from tkinter import ttk
from pi.editor import Editor


class Frame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(expand=True, fill=tk.BOTH)
        self.top = tk.Text(self, height=1, bd=0, highlightthickness=0, bg="#dddddd")
        self.top.pack(fill=tk.X)
        self.body = tk.Frame(self)
        self.body.pack(expand=True, fill=tk.BOTH)
        self.bottom = tk.Text(self, height=1, bd=0, highlightthickness=0, bg="#dddddd")
        self.bottom.config(state="disabled")
        self.bottom.pack(fill=tk.X)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Layout")
    style = ttk.Style()
    style.configure(".", font=("Noto Sans", 12))
    root.option_add("*Font", ("Noto Sans", 12))
    frame = Frame(root)
    frame.top.insert("1.0", "/home/nishant/src/pi/layout.py | Del Cut Paste Copy Look Undo ")
    frame.bottom.config(state="normal")
    frame.bottom.insert("1.0", "1,1  Mouse")
    frame.bottom.config(state="disabled")
    window = Editor(frame.body)
    lines = ["Hello, world!", str(), "Thanks for using Pi. Have a great day!"]
    for line in lines:
        window.editor.insert(tk.END, line + "\n")
    root.mainloop()
