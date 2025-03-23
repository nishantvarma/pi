import tkinter as tk

from tkinter import filedialog, Listbox, Menu, messagebox, simpledialog, ttk

from pi.config import config
from pi.core import exec_with_return, Folder
from pi.utils import quit, restart


class Console:
    def __init__(self, parent, prompt):
        self.buffer = str()
        self.prompt = prompt
        self.frame = ttk.Frame(parent)
        self.output = tk.Text(self.frame, state=tk.DISABLED, height=10)
        self.output.pack(fill=tk.BOTH, padx=4, pady=(4, 0))
        self.label = tk.Label(self.frame, text="Python")
        self.label.pack(side=tk.LEFT, padx=4)
        self.input = tk.Entry(self.frame)
        self.input.pack(fill=tk.X, side=tk.LEFT, expand=True, pady=4)
        self.input.bind("<Control-l>", self.clear)
        self.frame.bind("<Enter>", lambda event: self.input.focus_set())
        self.input.bind("<Return>", self.execute)
        self.button = ttk.Button(self.frame, text="Restart", command=restart)
        self.button.pack(side=tk.RIGHT, padx=4)
        self.button = ttk.Button(self.frame, text="Clear", command=self.clear)
        self.button.pack(side=tk.RIGHT, padx=4)
        self.apply_theme()
        self.locals = {}

    def apply_theme(self):
        self.output.config(
            bg=config.console.output_bg,
            inactiveselectbackground=config.console.output_select_bg
        )
        self.input.config(
            bg=config.console.input_bg,
            selectbackground=config.console.input_select_bg
        )

    def write(self, message):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, message)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def execute(self, event=None):
        command = self.input.get().strip()
        self.input.delete(0, tk.END)
        if command:
            self.write(self.prompt + command + "\n")
            result = exec_with_return(command, globals(), self.locals)
            if result is not None:
                self.write(str(result) + "\n")

    def clear(self, event=None):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    def readline(self, prompt="Value"):
        return simpledialog.askstring("Input", prompt)


