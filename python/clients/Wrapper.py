import socket
from enum import Enum
import json


class State(Enum):
    SIZE = 0
    DATA = 1


class Wrapper:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect(("localhost", 6969))
        self.sock.setblocking(False)
        self.state = State.SIZE
        self.buffer = b''
        self.bufferSize = 4

    def receive(self):
        try:
            tmpBuffer = self.sock.recv(self.bufferSize - len(self.buffer))
        except BlockingIOError:
            return None
        if len(tmpBuffer) == 0:
            raise IOError
        self.buffer += tmpBuffer
        if len(self.buffer) == self.bufferSize:
            if self.state == State.SIZE:
                self.bufferSize = int.from_bytes(self.buffer, "big")
                self.state = State.DATA
                self.buffer = b''
                return self.receive()
            else:
                print(self.buffer)
                x = json.loads(self.buffer)
                self.state = State.SIZE
                self.bufferSize = 4
                self.buffer = b''
                return x
        else:
            return None

    def send(self, msg):
        x = bytes(json.dumps(msg), "utf-8")
        size = len(x).to_bytes(4, "big")
        self.sock.sendall(size)
        self.sock.sendall(x)

    def close(self):
        self.sock.close()
