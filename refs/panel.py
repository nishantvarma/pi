#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk


class Panel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VS Code Like Left Panel")
        self.geometry("300x400")
        self.left_panel = tk.Frame(self, bg="#2c2c2c", width=50)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.icons = ["🏠", "📁", "🔍", "🔧", "📜"]
        for icon in self.icons:
            btn = tk.Button(self.left_panel, text=icon, bg="#333", fg="white", font=("Arial", 14), bd=0)
            btn.pack(pady=10, padx=5, fill=tk.X)
        self.content = tk.Frame(self, bg="#1e1e1e")
        self.content.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        label = tk.Label(self.content, text="Main Content Area", bg="#1e1e1e", fg="white")
        label.pack(pady=20)


if __name__ == "__main__":
    app = Panel()
    app.mainloop()
