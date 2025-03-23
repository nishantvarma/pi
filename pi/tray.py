#!/usr/bin/env python

import psutil
import time
import tkinter as tk


class Tray(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="x", anchor="e")
        self.clock_label = tk.Label(self)
        self.clock_label.pack(side="right", padx=(0, 4), pady=4)
        self.charge_label = tk.Label(self)
        self.charge_label.pack(side="right", padx=(0, 2))
        self.percent_label = tk.Label(self)
        self.percent_label.pack(side="right", padx=2)
        self.after(1000, self.refresh)

    def refresh(self):
        self.update_clock()
        self.update_battery()
        self.after(1000, self.refresh)

    def update_clock(self):
        self.clock_label.config(text=time.strftime("%H:%M:%S"))

    def update_battery(self):
        battery = psutil.sensors_battery()
        if not battery:
            return
        plugged = battery.power_plugged
        percent = battery.percent
        self.percent_label.config(text=f"{int(percent)}%")
        color = "green" if percent > 50 else "orange" if percent > 20 else "red"
        self.charge_label.config(text="⬆" if plugged else "⬇", fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tray")
    root.geometry("250x50")
    root.configure(bg="white")
    widget = Tray(root)
    root.mainloop()
