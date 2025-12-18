import atexit
import os
import socket
import threading

SOCKET_PATH = "/tmp/pi.sock"
sock = None


def is_running():
    if not os.path.exists(SOCKET_PATH):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(SOCKET_PATH)
        s.send(b"ping")
        s.close()
        return True
    except:
        try:
            os.remove(SOCKET_PATH)
        except:
            pass
        return False


def send(path):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCKET_PATH)
    s.send(path.encode())
    s.close()


def cleanup():
    global sock
    if sock:
        sock.close()
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)


def start(callback):
    global sock
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    sock.listen(5)
    atexit.register(cleanup)

    def listen():
        while True:
            try:
                conn, _ = sock.accept()
                path = conn.recv(4096).decode()
                if path and path != "ping":
                    callback(path)
                conn.close()
            except:
                break

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
