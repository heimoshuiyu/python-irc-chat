import socket

from message import Message, NumericReplyMessage


class Connection:
    def __init__(self, conn):
        self.conn = conn
        self.addr = conn.getpeername()
        self.nickname = None
        self.buff = b''

    def receiveMessage(self) -> Message:
        if not b'\n\r' in self.buff:
            try:
                self.buff += self.conn.recv(1024)
            except socket.error:
                return None
        if b'\n\r' in self.buff:
            message, self.buff = self.buff.split(b'\n\r', 1)
            return Message(message.decode('utf-8'))
        else:
            self.buff = b''
            return None

    def sendMessage(self, message: Message):
        self.conn.sendall(message.encode())

    def sendMessageWithPrefix(self, prefix: str, message: Message):
        message.prefix = prefix
        self.conn.sendall(message.encode())

    def close(self):
        self.conn.close()
