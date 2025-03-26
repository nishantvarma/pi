#!/usr/bin/env python

import tkinter as tk

class FloatingMenu(tk.Canvas):
    def __init__(self, parent, items, x=0, y=0):
        super().__init__(parent, width=100, height=len(items) * 20 + 8, bg="white", highlightthickness=1, bd=0)
        self.place(x=x, y=y)
        for i, item in enumerate(items):
            text_id = self.create_text(50, 5 + i * 20, text=item, font=("Arial", 10), fill="black", tags=item)
            self.tag_bind(text_id, "<Enter>", lambda e, t=text_id: self.itemconfig(t, fill="gray"))
            self.tag_bind(text_id, "<Leave>", lambda e, t=text_id: self.itemconfig(t, fill="black"))
            self.tag_bind(text_id, "<Button-1>", lambda e, t=item: self.select_item(t))

    def select_item(self, name):
        print(f"Selected: {name}")
        self.destroy()

def toggle_menu(event=None):
    global menu
    if menu: 
        menu.destroy()
        menu = None
    else:
        x, y = menu_button.winfo_x(), menu_button.winfo_y() + menu_button.winfo_height()
        menu = FloatingMenu(root, ["New", "Open", "Save", "Exit"], x, y)

def drag_start(event):
    menu_button.startX, menu_button.startY = event.x, event.y

def drag_move(event):
    x = menu_button.winfo_x() + event.x - menu_button.startX
    y = menu_button.winfo_y() + event.y - menu_button.startY
    menu_button.place(x=x, y=y)

root = tk.Tk()
root.geometry("250x150")
menu_button = tk.Button(root, text="☰", command=toggle_menu)
menu_button.place(x=20, y=20)
menu_button.bind("<ButtonPress-1>", drag_start)
menu_button.bind("<B1-Motion>", drag_move)

menu = None
root.mainloop()
