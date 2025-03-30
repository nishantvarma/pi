#!/usr/bin/env python

import tkinter as tk


class List(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        #self.tag_configure("sel", background="#d3d3d3")
        #self.tag_configure("sel", background="#ffffae")
        self.bind("<ButtonPress-1>", self.mouse_select_press)
        # self.bind("<B1-Motion>", self.mouse_select_update)
        self.bind("<ButtonRelease-1>", self.mouse_select_release)
        #self.bind("<Control-Button-1>", self.mouse_append)
        #self.bind("<Down>", self.navigate)
        #self.bind("<Shift-Down>", self.navigate)
        #self.bind("<Shift-Up>", self.navigate)
        #self.bind("<Up>", self.navigate)
        #self.bind("a", self.append_line)
        #self.bind("s", self.select_line)
        #self.selected_lines = set()
        #self.current_line = "1"

    def select_line(self):
        self.tag_remove("sel", "1.0", "end")
        self.tag_add("sel", f"{self.press_line}.0", f"{int(self.press_line) + 1}.0")

    def select_block(self):
        self.tag_add("sel", f"{self.press_line}.0", f"{self.current_line + 1}.end + 1c")

    def append_line(self, event=None):
        self.selected_lines.add(self.current_line)
        #self.update_selection()

    def mouse_select_press(self, event=None):
        self.tag_remove("sel", "1.0", "end")
        self.press_index = self.index(f"@{event.x},{event.y}")
        self.press_line = int(self.press_index.split(".")[0])
        # self.current_index = self.index(f"@{event.x},{event.y}")
        # self.current_line = int(self.current_index.split(".")[0])
        # self.select_line()
        return "break"

    def mouse_select_update(self, event=None):
        # self.current_index = self.index(f"@{event.x},{event.y}")
        # self.current_line = int(self.current_index.split(".")[0])
        # self.select_block()
        return "break"

    def mouse_select_release(self, event=None):
        self.current_index = self.index(f"@{event.x},{event.y}")
        self.current_line = int(self.current_index.split(".")[0])
        self.select_block()
        return "break"

    def mouse_append(self, event):
        self.current_line = str(int(self.index(f"@{event.x},{event.y}").split(".")[0]))
        self.focus_set()
        self.append_line()

    def navigate(self, event):
        append = event.state & 0x0001
        new_line = int(self.current_line)
        if event.keysym == "Down":
            new_line += 1
        elif event.keysym == "Up":
            new_line -= 1
        if 1 <= new_line <= int(self.index("end-1c").split(".")[0]):
            self.current_line = str(new_line)
            if append:
                self.append_line()
            else:
                self.select_line()
            return "break"

    def update_selection(self):
        self.tag_remove("selected", "1.0", "end")
        for line in self.selected_lines:
            self.tag_add("selected", f"{line}.0", f"{line}.end + 1c")


if __name__ == "__main__":
    root = tk.Tk()
    text = List(root)
    text.pack(fill=tk.BOTH, expand=True)
    text.configure(state="normal")
    text.insert("1.0", "\n".join([f"Hello, line {i}" for i in range(1, 21)]) + "\n")
    # text.configure(state="disabled")
    root.mainloop()
