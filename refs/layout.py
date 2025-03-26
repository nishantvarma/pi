#!/usr/bin/env python

import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Editor")
    root.option_add("*Font", ("DejaVu Sans Mono", 11))
    main = tk.Frame(root)
    main.pack(fill=tk.BOTH, expand=True)
    top = tk.Text(main, height=1, bg="#d3d3d3", bd=0, relief="flat", highlightthickness=0)
    top.pack(fill=tk.X)
    top.insert("1.0", "/home/nishant/src/pi/pi.py | Del Cut Paste Snarf Look Undo ")
    body = tk.Frame(main)
    body.pack(fill=tk.BOTH, expand=True)
    tag = tk.Text(body, height=1, bg="#ffffea", bd=1, relief="flat", highlightthickness=0)
    tag.pack(fill=tk.X)
    tag.insert("1.0", "/home/nishant/src/pi/pi.py | Del Cut Paste Snarf Look Undo ")
    editor = tk.Text(body, bd=0, relief="flat", highlightthickness=0)
    editor.pack(fill=tk.BOTH, expand=True)
    editor.insert("1.0", "Hello, World.\n\nThanks for using Pi. Have a good day!\n")
    bottom = tk.Text(main, height=1, bg="#d3d3d3", bd=0, relief="flat", highlightthickness=0)
    bottom.pack(fill=tk.X)
    bottom.insert("1.0", "1,1  All")
    bottom.config(state="disabled")
    root.mainloop()


if __name__ == "__main__":
    main()
