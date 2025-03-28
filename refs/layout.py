#!/usr/bin/env python

import tkinter as tk


class Editor(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(expand=True, fill=tk.BOTH)
        self.editor = tk.Text(self, bd=0, highlightthickness=0)
        self.editor.pack(expand=True, fill=tk.BOTH)


class Frame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self.top = tk.Text(self, height=1, bg="#dddddd", bd=0, highlightthickness=0)
        self.top.pack(fill=tk.X)
        self.body = tk.Frame(self)
        self.body.pack(fill=tk.BOTH, expand=True)
        self.bottom = tk.Text(self, height=1, bg="#dddddd", bd=0, highlightthickness=0)
        self.bottom.config(state="disabled")
        self.bottom.pack(fill=tk.X)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Editor")
    root.option_add("*Font", ("Sans", 11))
    frame = Frame(root)
    frame.top.insert("1.0", "/home/nishant/src/pi/pi.py | Del Cut Paste Copy Look Undo ")
    frame.bottom.config(state="normal")
    frame.bottom.insert("1.0", "1,1  All")
    frame.bottom.config(state="disabled")
    window = Editor(frame.body)
    lines = ["Hello, World.", str(), "Thanks for using Pi. Have a good day!"]
    for line in lines:
        window.editor.insert(tk.END, line + "\n")
    root.mainloop()
