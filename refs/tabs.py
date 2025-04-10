import tkinter as tk
from tkinter import font

class CleanTabs:
    def __init__(self, root):
        self.root = root
        self.tabs = []
        self.text_widgets = {}
        self.active_tab = None
        self.drag_tab = None

        self.font = font.Font(family="Noto Sans", size=11)

        self.tab_frame = tk.Frame(root, bg="white")
        self.tab_frame.pack(fill="x", side="top")

        self.tab_bar = tk.Text(
            self.tab_frame, height=1, wrap="none", font=self.font,
            bg="white", bd=0, relief="flat", highlightthickness=0, spacing3=5
        )
        self.tab_bar.pack(fill="x", side="top")
        self.tab_bar.config(cursor="arrow", state="disabled")

        self.separator = tk.Frame(self.tab_frame, height=1, bg="black", bd=0)
        self.separator.pack(fill="x", side="bottom")

        self.editor_area = tk.Frame(root, bg="white")
        self.editor_area.pack(fill="both", expand=True)

        self.tab_bar.bind("<Button-1>", self.on_click)
        self.tab_bar.bind("<B1-Motion>", lambda e: "break")  # disable text selection while dragging
        self.tab_bar.bind("<ButtonRelease-1>", self.on_drop)
        self.tab_bar.bind("<Button-2>", self.on_middle_click)
        self.tab_bar.bind("<Button-3>", self.on_middle_click)

        root.bind("<Control-Tab>", self.next_tab)
        root.bind("<Control-Shift-Tab>", self.prev_tab)
        root.bind("<Control-Next>", self.next_tab)
        root.bind("<Control-Prior>", self.prev_tab)

        self.add_tab("tab1")
        self.add_tab("tab2")

    def add_tab(self, name=None):
        if not name:
            name = self.auto_name()
        self.tabs.append(name)
        self.text_widgets[name] = self.create_editor(name)
        self.redraw_tabs()
        self.switch_tab(name)

    def auto_name(self):
        i = 1
        while f"tab{i}" in self.tabs:
            i += 1
        return f"tab{i}"

    def create_editor(self, name):
        editor = tk.Text(
            self.editor_area, wrap="word", undo=True,
            font=self.font, bg="white", relief="flat", bd=0, highlightthickness=0
        )
        editor.insert("1.0", f"This is {name}.")
        editor.place(x=0, y=0, relwidth=1, relheight=1)  # <- use place
        return editor

    def redraw_tabs(self):
        self.tab_bar.config(state="normal")
        self.tab_bar.delete("1.0", "end")

        for name in self.tabs:
            display = f" {name} "
            self.tab_bar.insert("end", display)
            start = self.tab_bar.index("insert - %dc" % len(display))
            end = self.tab_bar.index("insert")
            self.tab_bar.tag_add(name, start, end)

            if name == self.active_tab:
                self.tab_bar.tag_config(
                    name,
                    foreground="black",
                    underline=True,
                    spacing1=0,
                    spacing3=3
                )
            else:
                self.tab_bar.tag_config(
                    name,
                    foreground="black",
                    underline=False,
                    spacing1=0,
                    spacing3=3
                )

        # Add "+" tab
        self.tab_bar.insert("end", "  +  ")
        start = self.tab_bar.index("insert - 5c")
        end = self.tab_bar.index("insert")
        self.tab_bar.tag_add("+", start, end)
        self.tab_bar.tag_config("+", foreground="gray", underline=False)

        self.tab_bar.config(state="disabled")

    def get_tab_under_cursor(self, event):
        index = self.tab_bar.index(f"@{event.x},{event.y}")
        for name in self.tabs + ["+"]:
            if self.tab_bar.tag_ranges(name):
                start, end = self.tab_bar.tag_ranges(name)
                if self.tab_bar.compare(index, ">=", start) and self.tab_bar.compare(index, "<", end):
                    return name
        return None

    def on_click(self, event):
        name = self.get_tab_under_cursor(event)
        if name == "+":
            self.add_tab()
        elif name:
            self.drag_tab = name

    def on_drop(self, event):
        drop_tab = self.get_tab_under_cursor(event)
        if self.drag_tab and drop_tab and self.drag_tab != drop_tab and drop_tab in self.tabs:
            from_idx = self.tabs.index(self.drag_tab)
            to_idx = self.tabs.index(drop_tab)
            self.tabs.insert(to_idx, self.tabs.pop(from_idx))
            self.redraw_tabs()
        elif self.drag_tab and self.drag_tab in self.tabs:
            self.switch_tab(self.drag_tab)
        self.drag_tab = None

    def on_middle_click(self, event):
        name = self.get_tab_under_cursor(event)
        if name in self.tabs:
            self.close_tab(name)

    def close_tab(self, name):
        if name in self.tabs:
            self.tabs.remove(name)
            widget = self.text_widgets.pop(name)
            widget.destroy()
            if self.active_tab == name:
                self.active_tab = self.tabs[0] if self.tabs else None
                if self.active_tab:
                    self.text_widgets[self.active_tab].pack(fill="both", expand=True)
            self.redraw_tabs()

    def switch_tab(self, name):
        if name not in self.text_widgets:
            return
        self.text_widgets[name].tkraise()  # <- use tkraise instead of pack_forget/pack
        self.active_tab = name
        self.redraw_tabs()

    def next_tab(self, event=None):
        if self.active_tab in self.tabs:
            i = self.tabs.index(self.active_tab)
            i = (i + 1) % len(self.tabs)
            self.switch_tab(self.tabs[i])

    def prev_tab(self, event=None):
        if self.active_tab in self.tabs:
            i = self.tabs.index(self.active_tab)
            i = (i - 1) % len(self.tabs)
            self.switch_tab(self.tabs[i])

root = tk.Tk()
root.geometry("800x500")
root.title("Clean Underline Tabs")
root.configure(bg="white")
CleanTabs(root)
root.mainloop()
