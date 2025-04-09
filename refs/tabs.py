import tkinter as tk

class DragReorderTabs:
    def __init__(self, root):
        self.root = root
        self.tabs = []
        self.text_widgets = {}
        self.active_tab = None
        self.drag_tab = None

        # Full-width, no-border tab area
        self.tab_frame = tk.Frame(root, bg="white", highlightthickness=0, bd=0)
        self.tab_frame.pack(fill="x")

        self.tab_canvas = tk.Canvas(self.tab_frame, height=24, bg="white", highlightthickness=0, bd=0)
        self.tab_canvas.pack(fill="x", expand=True)

        self.tab_bar = tk.Text(
            self.tab_canvas, height=1, wrap="none", bg="white", relief="flat",
            font=("TkDefaultFont", 10), borderwidth=0, highlightthickness=0
        )
        self.tab_bar.configure(state="disabled", cursor="hand2")
        self.tab_canvas.create_window((0, 0), window=self.tab_bar, anchor="nw")

        # Black 1px bottom separator
        tk.Frame(self.tab_frame, height=1, bg="black").pack(fill="x", side="bottom")

        self.editor_area = tk.Frame(root, bg="white")
        self.editor_area.pack(fill="both", expand=True)

        # Mouse bindings
        self.tab_bar.bind("<Button-1>", self.on_click)
        self.tab_bar.bind("<ButtonRelease-1>", self.on_drop)
        self.tab_bar.bind("<Button-2>", self.on_middle_click)
        self.tab_bar.bind("<Button-3>", self.on_middle_click)

        # Initial tabs
        self.add_tab("tab1")
        self.add_tab("tab2")
        self.add_tab("tab3")

    def add_tab(self, name=None):
        if not name:
            name = self.auto_name()
        self.tabs.append(name)
        self.text_widgets[name] = self.create_editor(name)
        self.redraw_tabs()
        self.switch_tab(name)

    def auto_name(self):
        base = "tab"
        i = 1
        while f"{base}{i}" in self.tabs:
            i += 1
        return f"{base}{i}"

    def create_editor(self, name):
        text = tk.Text(self.editor_area, wrap="word", bg="white", relief="flat", undo=True, bd=0)
        text.insert("1.0", f"This is {name}.")
        text.pack_forget()
        return text

    def redraw_tabs(self):
        self.tab_bar.config(state="normal")
        self.tab_bar.delete("1.0", "end")
        for name in self.tabs:
            self.tab_bar.insert("end", f"{name} ")
            start = self.tab_bar.index("insert - %dc" % (len(name) + 1))
            end = self.tab_bar.index("insert -1c")
            self.tab_bar.tag_add(name, start, end)
            self.tab_bar.tag_config(name, background="white")
        self.tab_bar.insert("end", "+")
        self.tab_bar.tag_add("PLUS", "end-2c", "end-1c")
        self.tab_bar.tag_config("PLUS", foreground="gray", background="white")

        if self.active_tab in self.tabs:
            self.tab_bar.tag_config(self.active_tab, background="#ddd")
        self.tab_bar.config(state="disabled")

    def get_tab_under_cursor(self, event):
        index = self.tab_bar.index(f"@{event.x},{event.y}")
        for name in self.tabs + ["PLUS"]:
            if self.tab_bar.tag_ranges(name):
                start, end = self.tab_bar.tag_ranges(name)
                if self.tab_bar.compare(index, ">=", start) and self.tab_bar.compare(index, "<", end):
                    return name
        return None

    def on_click(self, event):
        name = self.get_tab_under_cursor(event)
        if name == "PLUS":
            self.add_tab()
        else:
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
        if name and name in self.tabs:
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
        if self.active_tab:
            self.text_widgets[self.active_tab].pack_forget()
        self.text_widgets[name].pack(fill="both", expand=True)
        self.active_tab = name
        self.redraw_tabs()


root = tk.Tk()
root.geometry("800x500")
root.title("Minimal Tab Manager")
root.configure(bg="white")
DragReorderTabs(root)
root.mainloop()
