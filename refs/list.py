#!/usr/bin/env python

import tkinter as tk

class List(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<ButtonPress-1>", self.mouse_select_press)
        self.bind("<B1-Motion>", self.mouse_select_update) 
        self.bind("<ButtonRelease-1>", self.mouse_select_release)

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
        self.current_index = self.index(f"@{event.x},{event.y}")
        self.current_line = int(self.current_index.split(".")[0])
        if hasattr(self, "select_block_after"):
            self.after_cancel(self.select_block_after)
        self.select_block_atfer = self.after(10, self.select_block)
        return "break"

    def mouse_select_release(self, event=None):
        self.mouse_select_update(event)
        return "break"


if __name__ == "__main__":
    root = tk.Tk()
    text = List(root)
    text.pack(fill=tk.BOTH, expand=True)
    text.insert("1.0", "\n".join([f"Hello, line {i}" for i in range(1, 21)]) + "\n")
    root.mainloop()
