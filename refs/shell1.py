import os
import pty
import select
import sys
import termios
import tkinter as tk
import threading

from tkinter.scrolledtext import ScrolledText


def configure_pty(fd):
    attrs = termios.tcgetattr(fd)
    attrs[3] &= ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, attrs)


class ShellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PTY Shell")
        self.text_area = ScrolledText(root, wrap=tk.WORD, height=20, width=80)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.entry = tk.Entry(root)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<Return>", self.send_command)
        self.master, self.slave = pty.openpty()
        self.pid = os.fork()
        if self.pid == 0:
            os.setsid()
            os.dup2(self.slave, 0)
            os.dup2(self.slave, 1)
            os.dup2(self.slave, 2)
            os.close(self.master)
            configure_pty(self.slave)
            os.execlp("rc", "rc")
        else:
            os.close(self.slave)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.read_thread = threading.Thread(target=self.read_output)
            self.read_thread.daemon = True
            self.read_thread.start()

    def send_command(self, event):
        command = self.entry.get() + "\n"
        os.write(self.master, command.encode())
        self.entry.delete(0, tk.END)

    def read_output(self):
        while True:
            try:
                rlist, _, _ = select.select([self.master], [], [])
                if self.master in rlist:
                    output = os.read(self.master, 4096)
                    self.text_area.insert(tk.END, output.decode().strip())
                    self.text_area.see(tk.END)
            except OSError:
                break

    def on_close(self):
        os.kill(self.pid, 9)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShellApp(root)
    root.mainloop()
