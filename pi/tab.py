from tkinter import ttk


class Tab(ttk.Notebook):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.enable_traversal()
        self.parent = parent
        self.dragged = None
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-2>", self.close)
        self.bind("<Button-3>", self.parent.duplicate_tab)

    def on_press(self, event):
        try:
            self.dragged = self.index(f"@{event.x},{event.y}")
        except:
            pass

    def on_release(self, event):
        if not hasattr(self, "dragged"):
            return
        source = self.dragged
        del self.dragged
        try:
            target = self.index(f"@{event.x},{event.y}")
        except:
            return
        if target != source:
            self.insert(target, self.tabs()[source])
        self.parent.tab_activated()

    def close(self, event=None):
        if event:
            tab = self.tabs()[self.index(f"@{event.x},{event.y}")]
        else:
            tab = self.select()
        if len(self.tabs()) > 1:
            self.forget(tab)
            self.parent.data.pop(tab)
            self.parent.tab_activated()
