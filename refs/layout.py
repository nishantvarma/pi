#!/usr/bin/env python

import tkinter as tk

from tkinter import ttk

root = tk.Tk()
root.title("Pi")
root.geometry("1000x650")

ICONS = {
    "menu": "≡",
    "explorer": "📁",
    "search": "🔍",
    "git": "⎇",
    "debug": "🛠",
}

top = tk.Frame(root)
top.pack(side=tk.TOP, fill=tk.X)

main = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#f3f3f3", sashwidth=6)
main.pack(fill=tk.BOTH, expand=True)

left_panel = tk.Frame(main, width=48, bg="#e8e8e8")
left_panel.pack_propagate(False)

menu_btn = tk.Button(
    left_panel,
    text=ICONS["menu"],
    font=("Ubuntu", 12),
    bg="#e8e8e8",
    fg="#000000",
    bd=0,
    activebackground="#d4d4d4",
)
menu_btn.pack(fill=tk.X, pady=(10, 5))

for icon_name in ["explorer", "search", "git", "debug"]:
    btn = tk.Button(
        left_panel,
        text=ICONS[icon_name],
        font=("Ubuntu", 12),
        bg="#e8e8e8",
        fg="#000000",
        bd=0,
        activebackground="#d4d4d4",
    )
    btn.pack(fill=tk.X, pady=3)

main.add(left_panel, stretch="never")

sidebar_pane = tk.PanedWindow(main, orient=tk.HORIZONTAL, sashwidth=6)
main.add(sidebar_pane)

sidebar = tk.Frame(sidebar_pane, width=250, bg="#f3f3f3")
sidebar.pack_propagate(False)

explorer_header = tk.Frame(sidebar, bg="#e4e4e4", height=30)
tk.Label(
    explorer_header, text="EXPLORER", bg="#e4e4e4", fg="#000000", font=("Segoe UI", 9)
).pack(side=tk.LEFT, padx=10)
explorer_header.pack(fill=tk.X)

tree = ttk.Treeview(sidebar, show="tree", selectmode="browse")
tree.pack(fill=tk.BOTH, expand=True)

for i in range(1, 4):
    folder = tree.insert("", "end", text=f"Project {i}", open=False)
    for j in range(1, 4):
        tree.insert(folder, "end", text=f"file_{i}_{j}.py")

sidebar_pane.add(sidebar)

editor_pane = tk.PanedWindow(sidebar_pane, orient=tk.VERTICAL, sashwidth=6)
sidebar_pane.add(editor_pane)

notebook = ttk.Notebook(editor_pane)
tab1 = tk.Frame(notebook, bg="#ffffff")
tab2 = tk.Frame(notebook, bg="#ffffff")

notebook.add(tab1, text="main.py")
notebook.add(tab2, text="README.md")

style = ttk.Style()

style.layout("Tab", [('Notebook.tab', {'sticky': 'nswe', 'children':
   [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
      [('Notebook.label', {'side': 'top', 'sticky': ''})],
   })],
})]
)

style.configure("Tab", focuscolor=style.configure(".")["background"])

editor_frame = tk.Frame(tab1, bg="#ffffff")
editor_frame.pack(fill=tk.BOTH, expand=True)

line_numbers = tk.Text(
    editor_frame,
    width=4,
    padx=4,
    pady=4,
    bg="#f5f5f5",
    fg="#444444",
    bd=0,
    font=("Consolas", 10),
)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

editor = tk.Text(
    editor_frame,
    wrap="none",
    bg="#ffffff",
    fg="#000000",
    insertbackground="black",
    bd=0,
    font=("Consolas", 10),
)
editor_scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=editor.yview)
editor.configure(yscrollcommand=editor_scroll.set)

editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

editor.insert("1.0", "Hello, World")
for i in range(2, 21):
    line_numbers.insert(f"{i}.0", f"{i}\n")

editor_pane.add(notebook)

console_frame = tk.Frame(editor_pane, height=150, bg="#ffffff")
console_frame.pack_propagate(False)

console_notebook = ttk.Notebook(console_frame)
terminal_tab = tk.Frame(console_notebook, bg="#ffffff")
problems_tab = tk.Frame(console_notebook, bg="#ffffff")
output_tab = tk.Frame(console_notebook, bg="#ffffff")

console_notebook.add(terminal_tab, text="Terminal")
console_notebook.add(problems_tab, text="Problems")
console_notebook.add(output_tab, text="Output")

terminal = tk.Text(
    terminal_tab, bg="#ffffff", fg="#000000", font=("Consolas", 10), wrap="word"
)
terminal.pack(fill=tk.BOTH, expand=True)
terminal.insert("1.0", "$ python main.py\nHello, World!\n\n")

console_notebook.pack(fill=tk.BOTH, expand=True)
editor_pane.add(console_frame)

status_bar = tk.Frame(root, bg="#444444", height=22)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

tk.Label(status_bar, text="main.py", bg="#444444", fg="white", padx=10, font=("Segoe UI", 9)).pack(side=tk.LEFT)
tk.Label(status_bar, text="UTF-8", bg="#444444", fg="white", padx=10, font=("Segoe UI", 9)).pack(side=tk.LEFT)
tk.Label(status_bar, text="Ln 1, Col 1", bg="#444444", fg="white", padx=10, font=("Segoe UI", 9)).pack(side=tk.LEFT)
tk.Label(status_bar, text="Python", bg="#444444", fg="white", padx=10, font=("Segoe UI", 9)).pack(side=tk.RIGHT)

if __name__ == "__main__":
    heading = tk.Label(top)
    heading.config(font=("Segoe UI", 9))
    heading.config(bg="#444444", fg="#ffffff")
    heading.config(text="Heading")
    heading.pack(fill=tk.X)
    root.mainloop()
