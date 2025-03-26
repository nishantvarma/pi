#!/usr/bin/env python

import tkinter as tk

class DraggableButton(tk.Button):
    def __init__(self, parent, text, index, move_callback, toggle_callback, *args, **kwargs):
        super().__init__(parent, text=text, *args, **kwargs)
        self.parent = parent
        self.index = index
        self.move_callback = move_callback
        self.toggle_callback = toggle_callback
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-1>", self.on_click)
        self.start_x = 0
        self.start_index = index
    
    def on_press(self, event):
        self.start_x = event.x_root
        self.start_index = self.index
    
    def on_drag(self, event):
        dx = event.x_root - self.start_x
        self.place(x=self.winfo_x() + dx)
        self.start_x = event.x_root
    
    def on_release(self, event):
        self.move_callback(self)
    
    def on_click(self, event):
        self.toggle_callback(self.cget("text"))

class Taskbar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=30, bg='gray')
        self.pack(fill=tk.X, side=tk.BOTTOM)
        self.buttons = []
        self.button_positions = []
        self.frames = {}
        self.init_frames(parent)
        self.init_buttons()
    
    def init_frames(self, parent):
        colors = {"Minimize": "lightblue", "Maximize": "lightgreen", "Close": "lightcoral"}
        for name, color in colors.items():
            frame = tk.Frame(parent, bg=color, width=300, height=170)
            frame.place(x=0, y=0)
            self.frames[name] = frame
        self.frames["Minimize"].tkraise()
    
    def init_buttons(self):
        for i, name in enumerate(["Minimize", "Maximize", "Close"]):
            btn = DraggableButton(self, text=name, index=i, move_callback=self.reorder_buttons, toggle_callback=self.toggle_frame)
            btn.place(x=i * 80, y=5, width=75, height=20)
            self.buttons.append(btn)
            self.button_positions.append(i * 80)
    
    def reorder_buttons(self, moved_btn):
        positions = sorted((btn.winfo_x(), btn) for btn in self.buttons)
        for i, (_, btn) in enumerate(positions):
            btn.index = i
            btn.place(x=i * 80, y=5)
    
    def toggle_frame(self, frame_name):
        frame = self.frames[frame_name]
        if frame.winfo_ismapped():
            frame.lower()  # Hide the frame
        else:
            frame.tkraise()  # Show the frame

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x200")
    taskbar = Taskbar(root)
    root.mainloop()
