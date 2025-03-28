#!/usr/bin/env python

import os
import pty
import select
import sys
import termios


def configure_pty(fd):
    attrs = termios.tcgetattr(fd)
    attrs[3] &= ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, attrs)


def spawn_shell():
    master, slave = pty.openpty()
    pid = os.fork()
    if pid == 0:
        os.setsid()
        os.dup2(slave, 0)
        os.dup2(slave, 1)
        os.dup2(slave, 2)
        os.close(master)
        configure_pty(slave)
        os.execlp("rc", "rc")
    else:
        os.close(slave)
        while True:
            try:
                rlist, _, _ = select.select([sys.stdin, master], [], [])
                if sys.stdin in rlist:
                    command = sys.stdin.readline()
                    os.write(master, command.encode())
                if master in rlist:
                    output = os.read(master, 4096)
                    sys.stdout.buffer.write(output)
                    sys.stdout.flush()
            except KeyboardInterrupt:
                break


spawn_shell()
