'''
本文件以 IRC 协议为原型定义了报文结构
伪 BNF 如下

<message> ::= [':' <prefix> <空格>] <command> <params> '\n\r'
<command> 为大写英文单词或三位标识状态的整数字符串（用于回复）
<params> 为用空格分割的参数列表 ':'后到'\n\r'前的所有字符串视作一个参数
<target> 报文目标地址。可以为用户的暱称 <nickname> 或频道名称 <channel>
<channel> 以 '#' 开头以区分用户
'''

# 根据 TFC 1495 定义的部分状态码
NUMERIC_REPLIES = {
    'RPL_NONE': '300',
    'ERR_NEEDPASS': '410',
    'ERR_NONICKNAMEGIVEN': '431',
    'ERR_NICKNAMEINUSE': '433',
    'ERR_NOSUCHNICK': '401',
    'ERR_NOSUCHCHANNEL': '403',
    'ERR_NOTONCHANNEL': '442',
    'ERR_UNKNOWNCOMMAND': '421',
    'ERR_PASSWDMISMATCH': '464',
    'ERR_NICKCOLLISION': '436',
}


class Message:
    def __init__(self, message: str):
        '''输入 Message 字符串，解析字符串中各个部分的信息'''
        self.message = message

        self.prefix = None
        if message[0] == ':':
            self.prefix = message[1:message.index(' ')]
            message = message[message.index(' ') + 1:]

        if ' ' in message[1:]:
            self.command, self.params = message.split(' ', 1)
            if ':' in self.params:
                self.params, lastParam = self.params.split(':', 1)
                self.params = self.params.strip().split()
                self.params.append(lastParam)
            else:
                self.params = self.params.split(' ')
        else:
            self.command = message
            self.params = []

    def encode(self):
        '''将 Message 编码以进行发送'''
        for i in range(len(self.params)):
            if ' ' in self.params[i]:
                self.params[i] = ':' + self.params[i]
                break
        message = '{} {}'.format(self.command, ' '.join(self.params))
        if self.prefix:
            return ':{} {}'.format(self.prefix, message).encode('utf-8') + b'\n\r'
        else:
            return message.encode('utf-8') + b'\n\r'


def PassMessage() -> Message:
    return Message('PASS')


def NickMessage(nick: str, password="") -> Message:
    if password:
        return Message('NICK ' + nick + ' :' + password)
    return Message('NICK ' + nick)


def UserMessage(user: str, realname: str) -> Message:
    return Message('USER ' + user + ' 0 * :' + realname)


def JoinMessage(channel: str) -> Message:
    return Message('JOIN ' + channel)


def PrivmsgMessage(target: str, message: str) -> Message:
    return Message('PRIVMSG ' + target + ' :' + message)


def PartMessage(channel: str) -> Message:
    return Message('PART ' + channel)


def QuitMessage(message: str) -> Message:
    return Message('QUIT :' + message)


def NumericReplyMessage(numericReply: str, message: str) -> Message:
    return Message(':Server ' + NUMERIC_REPLIES[numericReply] + ' :' + message)
