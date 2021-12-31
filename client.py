import socket
import threading

from message import Message, PassMessage, NickMessage, JoinMessage, PrivmsgMessage, QuitMessage, PartMessage, NUMERIC_REPLIES
from connection import Connection

# import windows object and hook input and output
from gui import window
print = window.terminal.printToTerminal
input = window.getInput


class Client:
    def __init__(self, host, port, nickname, password=""):
        '''
        初始化客户端对象，建立和服务器的链接并进行握手
j
        - nickname 需要为不包含空格和:符号的用户暱称，
        暱称作为用户唯一识别符号，参见 RFC 1495 
        '''
        self.host = host
        self.port = port
        self.nickname = nickname
        self.password = password
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.host, self.port))
        self.connection = Connection(conn)

        # 客户端-服务器握手，参见 RFC 1459 4.1 Connection Registration
        self.Pass('password')
        self.Nick(self.nickname, self.password)

    def Pass(self, password: str):
        self.connection.sendMessage(PassMessage())

    def Nick(self, nickname: str, password=""):
        self.connection.sendMessage(NickMessage(nickname, password))

    def Join(self, channel: str):
        self.connection.sendMessage(JoinMessage(channel))

    def Part(self, channel: str):
        self.connection.sendMessage(Message('PART ' + channel))

    def Quit(self):
        self.connection.sendMessage(QuitMessage('Bye!'))

    def Send(self, target: str, message: str):
        self.connection.sendMessage(PrivmsgMessage(target, message))

    def startPrint(self):
        while True:
            message = self.connection.receiveMessage()
            if not message:
                break
            if message.command == 'PRIVMSG':
                if message.prefix == self.nickname:
                    continue
                prefix = ''
                if message.prefix:
                    prefix = '[%s] ' % message.prefix
                print(prefix + "-> [%s]: %s" %
                      (message.params[0], message.params[1]))
            elif isInt(message.command):
                print('[Server reply] %s: %s' %
                      (message.command, message.params[0]))
            elif message.command == 'JOIN':
                print('[%s] has joined the [%s] channel' %
                      (message.prefix, message.params[0]))
            elif message.command == 'PART':
                print('[%s] has left the [%s] channel' %
                      (message.prefix, message.params[0]))
            elif message.command == 'QUIT':
                reason = '' or message.params[0]
                print('[%s] has quit %s' % (message.prefix, reason))
            elif message.command == 'NICK':
                print('[%s] is now known as [%s]' %
                      (message.prefix, message.params[0]))
            else:
                print(message)


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def main():
    defaultTarget = None
    print('Welcome to the IRC client!')
    print('Please enter your nickname and password (optional):')
    # print('Format: /nick <nickname> [<password>]')
    nickname = input()
    password = ""
    if ' ' in nickname:
        nickname, password = nickname.split(' ', 1)
    print('Connecting to server at localhost on port 9999...')
    client = Client('localhost', 9999, nickname, password)
    threading.Thread(target=client.startPrint).start()
    print('Enter /help for help')
    while True:
        data = input()
        if not data:
            continue
        if data[0] == '/':
            dataList = data.split(' ')
            if dataList[0] == '/help':
                print('/nick <nickname> - change nickname')
                print('/join <channel> - join a channel')
                print('/part <channel> - part a channel')
                print('      Note: <channel> must start with #')
                print('/quit - quit the client')
                print('/msg <target> <message> - send a private message to a user')
                print('     Note: <target> can be a <nickname> or a <channel>')
            elif dataList[0] == '/quit':
                client.Quit()
                defaultTarget = None
                break
            elif dataList[0] == '/join':
                client.Join(dataList[1])
                defaultTarget = dataList[1]
            elif dataList[0] == '/part':
                client.Part(dataList[1])
                defaultTarget = None
            elif dataList[0] == '/msg':
                client.Send(dataList[1], ' '.join(dataList[2:]))
                defaultTarget = dataList[1]
            elif dataList[0] == '/nick':
                if len(dataList) == 3:
                    client.Nick(dataList[1], dataList[2])
                else:
                    client.Nick(dataList[1])
            else:
                print('Unknown command')
        else:
            if defaultTarget:
                client.Send(defaultTarget, data)


if __name__ == '__main__':
    # start main function in thread, so that the GUI can be used
    threading.Thread(target=main, daemon=True).start()
    # Tkinter must run at main thread
    window.mainloop()
