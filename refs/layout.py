#!/usr/bin/env python

import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Editor")

    main = tk.Frame(root)
    main.pack(fill=tk.BOTH, expand=True)

    font = ("DejaVu Sans Mono", 11)

    top = tk.Text(main, height=1, bg="#d3d3d3", bd=1, relief="flat", font=font)
    top.pack(fill=tk.X)
    top.insert("1.0", "/home/nishant/src/leaf/leaf.py New Del Cut Paste Snarf Get Look Font Put | ")

    body = tk.Text(main, font=font, bd=0, relief="flat", highlightthickness=0)
    body.pack(fill=tk.BOTH, expand=True)
    body.insert("1.0", "Hello, World.\n\nThis is the Leaf programmer's interface.")

    bottom = tk.Text(main, height=1, bg="#d3d3d3", bd=1, relief="flat", highlightthickness=0, font=font) 
    bottom.pack(fill=tk.X)
    bottom.insert("1.0", "1,1  All")
    bottom.config(state="disabled")

    root.mainloop()

if __name__ == "__main__":
    main()
