#!/usr/bin/env python

import tkinter as tk

from tkinter import ttk


class List(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.focus_set()
        self.bind("<ButtonPress-1>", self.mouse_select_press)
        self.bind("<B1-Motion>", self.mouse_select_update) 
        self.bind("<ButtonRelease-1>", self.mouse_select_release)
        self.bind("<Up>", self.key_up)
        self.bind("<Down>", self.key_down)

    def select_block(self):
        self.tag_remove("sel", "1.0", "end")
        if self.press_line <= self.current_line:
            self.tag_add("sel", f"{self.press_line}.0", f"{self.current_line}.end + 1c")
        else:
            self.tag_add("sel", f"{self.current_line}.0", f"{self.press_line}.end + 1c")

    def mouse_select_press(self, event=None):
        self.press_index = self.index(f"@{event.x},{event.y}")
        self.press_line = int(self.press_index.split(".")[0])
        return "break"

    def mouse_select_update(self, event=None):
        return "break"

    def mouse_select_release(self, event=None):
        self.current_index = self.index(f"@{event.x},{event.y}")
        self.current_line = int(self.current_index.split(".")[0])
        self.select_block()
        self.mark_set("insert", f"{self.current_line}.0")
        return "break"

    def key_up(self, event=None):
        breakpoint()
        index = self.index("insert")
        print(index)
        return
        line = int(index.split(".")[0])
        if line > 1:
            self.press_index = self.current_index = line
            self.select_block()
        return "break"

    def key_down(self, event=None):
        breakpoint()
        index = self.index("insert")
        print(index)
        return
        line = int(index.split(".")[0])
        max_line = int(self.index("end-1c").split(".")[0])
        if line < max_line:
            self.mark_set("insert", f"{line+1}.0")
        return "break"


if __name__ == "__main__":
    root = tk.Tk()
    root.option_add("*Font", ("Noto Sans", 11))
    style = ttk.Style()
    style.configure(".", font=("Noto Sans", 11))
    text = List(root)
    text.pack(fill=tk.BOTH, expand=True)
    text.insert("2.0", "\n".join([f"Hello, line {i}" for i in range(1, 4)]) + "\n")
    text.config(state="disabled")
    root.mainloop()
