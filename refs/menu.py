#!/usr/bin/env python

import tkinter as tk
from tkinter import font

class SamMenu(tk.Toplevel):
    def __init__(self, master, items, x, y):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="black", highlightthickness=1, highlightbackground="black")

        self.font = font.Font(family="Noto Sans", size=10)
        pad = 2
        self.items = items
        self.line_tags = {}

        width_chars = max(len(item) for item in items if item != "---") + 2 * pad

        self.text = tk.Text(
            self,
            font=self.font,
            bg="white",
            fg="black",
            width=width_chars,
            height=len(items),
            bd=0,
            padx=0,
            pady=2,
            relief="flat",
            wrap="none",
            highlightthickness=0,
            cursor="arrow",
        )
        self.text.pack()
        self.text.config(state="normal")

        for i, item in enumerate(items):
            if item == "---":
                display = "─" * (width_chars - 2)
                tag = f"sep_{i}"
                self.text.insert("end", display + "\n")
                self.text.tag_add(tag, f"{i+1}.0", f"{i+1}.end+1c")
                self.text.tag_configure(tag, foreground="#888888")
            else:
                padded = f"{' ' * pad}{item.lower()}{' ' * pad}"
                tag = f"item_{i}"
                self.line_tags[tag] = item
                self.text.insert("end", padded + "\n")
                self.text.tag_add(tag, f"{i+1}.0", f"{i+1}.end+1c")
                self.text.tag_bind(tag, "<Enter>", lambda e, t=tag: self.highlight(t))
                self.text.tag_bind(tag, "<Leave>", lambda e, t=tag: self.unhighlight(t))
                self.text.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.select(t))

        self.text.config(state="disabled")
        self.highlight(next(iter(self.line_tags)))

        self.geometry(f"+{x}+{y}")
        self.after(100, self._enable_global_close)
        self.bind("<Escape>", lambda e: self.destroy())
        self.text.bind("<Escape>", lambda e: self.destroy())
        self.text.bind("<FocusOut>", lambda e: self.destroy())

    def _enable_global_close(self):
        self.grab_set()
        self.master.bind("<Button-1>", self._click_outside, add="+")

    def _click_outside(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is None or not self.text.winfo_containing(event.x_root, event.y_root):
            self.destroy()

    def highlight(self, tag):
        self.text.config(state="normal")
        for t in self.line_tags:
            self.text.tag_configure(t, background="white", foreground="black")
        self.text.tag_configure(tag, background="black", foreground="white")
        self.text.config(state="disabled")

    def unhighlight(self, tag):
        pass

    def select(self, tag):
        print("Selected:", self.line_tags[tag])
        self.destroy()

def show_menu(event):
    global menu
    try:
        menu.destroy()
    except:
        pass

    items = [
        f"x: {event.x}",
        f"y: {event.y}",
        "---",
        "open",
        "close",
        "cancel"
    ]
    menu = SamMenu(root, items, event.x_root, event.y_root)

root = tk.Tk()
root.geometry("800x600")
root.configure(bg="white")
root.bind("<Button-3>", show_menu)
root.mainloop()
