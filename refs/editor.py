#!/usr/bin/python3.13

import tkinter as tk

from tkinter import filedialog

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "r") as f:
            text.delete(1.0, END)
            text.insert(END, f.read())

def save_file():
    file_path = filedialog.asksaveasfilename()
    if file_path:
        with open(file_path, "w") as f:
            f.write(text.get(1.0, tk.END))

root = tk.Tk()
root.title("Simple File Editor")
root.geometry("300x250")
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)
text = tk.Text(root)
text.pack(fill=tk.BOTH, expand=1)

root.mainloop()
