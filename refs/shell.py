#!/usr/bin/env python

import os
import subprocess
import threading

def read_output(process):
    while True:
        output = process.stdout.readline()
        if output:
            print(output.strip())
        if process.poll() is not None:
            break

process = subprocess.Popen(
    ["rc"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)
os.set_blocking(process.stdout.fileno(), False)

threading.Thread(target=read_output, args=(process,), daemon=True).start()

while True:
    command = input()
    if command.strip().lower() == "exit":
        process.terminate()
        break
    process.stdin.write(command + "\n")
    process.stdin.flush()
