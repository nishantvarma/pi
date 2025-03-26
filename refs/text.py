#!/usr/bin/env python

import tkinter as tk

def on_button_click():
    print("Button inside Text clicked!")

root = tk.Tk()
text = tk.Text(root, width=40, height=10)
text.pack()

# Insert some text
text.insert(tk.END, "Here is a Button: ")

# Create a button and embed it in the Text widget
btn = tk.Button(text, text="Click Me", command=on_button_click)
text.window_create(tk.END, window=btn)

# Insert text to separate the button and listbox
text.insert(tk.END, "\n\nHere is a Listbox:\n")

# Create a Listbox and embed it in the Text widget
listbox = tk.Listbox(text, height=3)
for item in ["Item 1", "Item 2", "Item 3"]:
    listbox.insert(tk.END, item)

text.window_create(tk.END, window=listbox)

root.mainloop()
