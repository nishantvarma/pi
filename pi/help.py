import tkinter as tk
from pi.config import config

inst = None
c = config.explorer


def toggle(parent, bindings):
    global inst
    if inst:
        try:
            inst.destroy()
        except:
            pass
        inst = None
        return
    inst = Help(parent, bindings)


class Help(tk.Toplevel):
    def __init__(self, parent, bindings):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.overrideredirect(True)
        self.configure(bg=c.select_bg)
        self.create(bindings)
        self.position()
        self.deiconify()
        self.after(100, self.bind_close)
        self.focus_set()

    def create(self, bindings):
        f = tk.Frame(self, bg=c.bg, padx=10, pady=10)
        f.pack(padx=1, pady=1)

        def label(txt, fg, col, anchor):
            l = tk.Label(f, text=txt, bg=c.bg, fg=fg, anchor=anchor)
            l.grid(row=i, column=col, sticky=anchor, padx=4)

        for i, (key, desc, _) in enumerate(bindings):
            label(key, c.broken_link_fg, 0, "e")
            label(desc, c.file_fg, 1, "w")

    def position(self):
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def bind_close(self):
        self.bind("<Key>", self.close)
        self.bind("<Button-1>", self.close)

    def close(self, event=None):
        global inst
        inst = None
        self.destroy()
