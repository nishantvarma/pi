#!/usr/bin/env python

import tkinter as tk


class Editor(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(expand=True, fill=tk.BOTH)
        self.editor = tk.Text(self, bd=0, highlightthickness=0)
        self.editor.pack(expand=True, fill=tk.BOTH)
