import socket
import threading

from connection import Connection
from message import NumericReplyMessage, Message
from database import Database


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(100)
        self.threads = []
        self.connDict = {}

    def run(self):
        while True:
            client, address = self.sock.accept()
            print(f'Connection from {address}')
            c = Connection(client)
            t = threading.Thread(
                target=self.handleConnection, args=(c,), daemon=True)
            t.start()
            self.threads.append(t)

    def vaildConnection(self, connection) -> int:
        # vaild connection from client
        message = connection.receiveMessage()
        if message is None or message.command != 'PASS':
            connection.sendMessage(NumericReplyMessage(
                'ERR_NEEDPASS', 'You need to send PASS first'))
            return 1

        message = connection.receiveMessage()
        if message is None or message.command != 'NICK':
            connection.sendMessage(NumericReplyMessage(
                'ERR_NONICKNAMEGIVEN', 'No nickname given'))
            return 4

        nickname = message.params[0]
        if nickname in self.connDict:
            connection.sendMessage(NumericReplyMessage(
                'ERR_NICKNAMEINUSE', 'Nickname already in use'))
            return 5

        userDb = Database('user.db')

        if len(message.params) == 1 and userDb.exists(nickname):
            connection.sendMessage(NumericReplyMessage(
                'ERR_NICKCOLLISION', 'Nickname already in use'))
            return 6

        if len(message.params) == 2:
            password = message.params[1]
            if not userDb.login(nickname, password):
                connection.sendMessage(NumericReplyMessage(
                    'ERR_PASSWDMISMATCH', 'Password mismatch'))
                return 6
            connection.sendMessage(
                Message(':NickServ PRIVMSG %s :Login successful' % nickname))
        else:
            connection.sendMessage(Message(
                ':NickServ PRIVMSG %s :Login as temporary user, set a password to register' % nickname))

        connection.nickname = nickname
        self.connDict[connection.nickname] = [connection]
        print('{} vailded and connected'.format(connection.nickname))
        return 0

    def handleConnection(self, connection):
        if self.vaildConnection(connection):
            connection.close()
            return
        while True:
            message = connection.receiveMessage()
            if message is None:
                self.handleQuit(connection)
                break
            if message.command == 'PRIVMSG':
                self.handlePrivMsg(connection, message)
            elif message.command == 'JOIN':
                self.handleJoin(connection, message)
            elif message.command == 'PART':
                self.handlePart(connection, message)
            elif message.command == 'QUIT':
                self.handleQuit(connection)
                break
            elif message.command == 'STAT':
                self.handleStat(connection, message)
            else:
                print('{} sent an invalid command {}'.format(
                    connection.nickname, message.command))
                connection.sendMessage(NumericReplyMessage(
                    'ERR_UNKNOWNCOMMAND', 'Unknown command'))
            print(message.message)

    def handleStat(self, connection, message):
        pass

    def handleQuit(self, connection):
        # remove connection from all channels and itself's record
        self.connDict[connection.nickname].remove(connection)
        if len(self.connDict[connection.nickname]) == 0:
            del self.connDict[connection.nickname]

        # remove connection from all channels
        for conns in self.connDict.values():
            if connection in conns:
                conns.remove(connection)
                for conn in conns:
                    # send quit message to all other connections
                    conn.sendMessageWithPrefix(connection.nickname,
                                               Message('QUIT :Socket disconnected'))
        print('{} disconnected'.format(connection.nickname))

    def handlePart(self, connection, message):
        target = message.params[0]
        if target[0] != '#':
            print('{} is not a channel'.format(target))
            connection.sendMessage(
                NumericReplyMessage('ERR_NOSUCHCHANNEL', target + ' is not a channel'))
            return
        if target not in self.connDict:
            print('you are not in {}'.format(target))
            connection.sendMessage(
                NumericReplyMessage('ERR_NOTONCHANNEL', 'You are not on channel'))
            return

        for conn in self.connDict[target]:
            conn.sendMessageWithPrefix(connection.nickname, message)
        if len(self.connDict[target]) == 0:
            del self.connDict[target]

        emptyChannel = []
        for name in self.connDict.keys():
            if name == connection.nickname:
                continue
            if connection in self.connDict[name]:
                self.connDict[name].remove(connection)
                if len(self.connDict[name]) == 0:
                    emptyChannel.append(name)
        for name in emptyChannel:
            del self.connDict[name]

        print(self.connDict)

    def handlePrivMsg(self, connection, message):
        target = message.params[0]
        if not target in self.connDict:
            print('{} is not online'.format(target))
            connection.sendMessage(
                NumericReplyMessage('ERR_NOSUCHNICK', 'No such nick'))
            return
        for conn in self.connDict[target]:
            if conn != connection:
                conn.sendMessageWithPrefix(connection.nickname, message)

    def handleJoin(self, connection, message):
        message.prefix = connection.nickname
        target = message.params[0]
        if target[0] != '#':
            print('{} is not a channel'.format(target))
            connection.sendMessage(
                NumericReplyMessage('ERR_NOSUCHCHANNEL', target + ' is not a channel'))
            return
        if target not in self.connDict:
            self.connDict[target] = []
        self.connDict[target].append(connection)
        for conn in self.connDict[target]:
            conn.sendMessageWithPrefix(connection.nickname, message)


if __name__ == '__main__':
    s = Server('127.0.0.1', 9999)
    print('Server is running at {}:{}'.format(s.host, s.port))
    s.run()
