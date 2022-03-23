# python-irc-chat

这是 networking 的课程作业。用 socket 技术实现 B/S 模式的聊天（支持私聊、群聊）。协议设计参考了 IRC。

## 依赖

- `python 3.x`
- `tkinter` 图形库（非必要）

## 使用

先启动服务端 `server.py`

再启动客户端 `client.py`

在客户端中输入 `<用户名> [<密码>]`，以空格分割，密码是可选的。如果使用密码，服务端将在数据库中记录用户昵称和密码，下次登录该用户需要使用相同的密码。

> 频道名称必须以井号 `#` 开头

- 客户端中输入 `/help` 可以查看命令帮助；
- 输入 `/msg nickname hello` 可以将消息 hello 发送给暱称为 nickname 的用户；
- 输入 `/join #channel` 可以加入名为 `#channel` 的频道，加入频道的用户将会收到来自该频道的消息，不存在的频道将会自动创建，没人的频道将会自动销毁。
- 输入 `/msg #channel hello` 可以将消息 hello 发送给在频道 `#channel` 里的所有用户。
- 输入 `/part #channel` 可以退出一个频道

如果输入的不是命令（不以 `/` 开头），则会自动认为这是一个 `/msg` 命令并发送到 `defaultTarget`

`/msg` `/join` `/part` 会改变 `defaultTarget`，也就是说，先输入 `/msg user hello` 给 user 发送了消息，之后接着向 user 发送消息都不需要输入前面的 `/msg user` 直接输入消息内容即可。

## 原理

一个完整的客户端向另一个客户端发送消息流程

1. 客户端向服务端使用 `/nick` 命令传递自己的昵称，表示上线

2. 服务端将用户昵称和链接储存在 `connDict` 字典中

3. 客户端向服务端使用 `/msg` 命令发送消息到指定的昵称

4. 服务端在内部维护的 `connDict` 字典中寻找目标链接

5. 服务端修改消息前缀 `prefix` 表示消息来源于此昵称

6. 服务端将修改后的消息发送给目标昵称

### 编程上一些实现细节

### `message.py`

定义了 `Message` 类，客户端向服务器发送、客户端从服务器接受的数据都是一个 `Message` 对象。这个类实现了消息的编码和解码。

- `Message(message: str)` 构建函数，传入一个字符串参数，该参数是从 socket 接收到的数据。

- `Message.prefix` 消息前缀，默认为空；如果消息前缀不为空，说明这是一条经过转发的消息（如服务器将他人的消息转发给你），prefix 为消息作者的 nickname

- `Message.command` IRC 命令

- `Message.params[]` 命令后面跟着的参数列表

- `Message.encode()` 编码消息，返回字节型数据，可以直接用于 socket 发送。

（不严格）按照 IRC 协议，下面用例子解释了 `message.py` 将消息编码后的样子

由用户 *miku* 发送消息 *hello world!* 给用户 rin（从 miku 客户端发送到服务器）🔽

```textile
PRIVMSG rin :hello world!
```

上条消息经过服务器转发给 *rin* 时，服务器会给消息带上前缀（prefix）表示消息来源方🔽

```textile
:miku PRIVMSG rin :hello world!
```

发送消息给名为 `#ch1` 的频道同理，只不过频道名称以 `#` 开头以此和用户区分🔽

```textile
PRIVMSG #ch1 :hello world!
```

其他在频道里的用户收到来自此频道的消息🔽

```textile
:miku PRIVMSG #ch1 :hello world!
```

### `connection.py`

稍稍封装了一下 socket connection。

- `Connection.receiveMessage() -> Message` 从 socket 链接中读出一个 `Message` 对象。

- `Connection.sendMessage(message: Message)` 将一个 `Message` 对象发送到 socket

- `Connection.sendMessageWithPrefix(prefix: str, message: Message)` 同上，只不过会带上 prefix

### `server.py`

- `Server.connDict{}`

储存 `Connection` 对象的字典。服务器中最关键的数据结构。服务器根据这个字典进行消息转发。

键代表 `nickname/channel`，值是一个列表，储存和这个 `nickname/channel` 相关的 `Connection` 对象。举个例子，服务器目前连接了三个用户，分别叫 `user1` `user2` `user3`，其中 `user1` 和 `user3` 加入了 `#channelA` 频道，`user1` 和 `user2` 加入了 `#channelB` 频道。结构类似

```json
{
    "user1": [<ConnectionToUser1>],
    "user2": [<ConnectionToUser2>],
    "user3": [<ConnectionToUser3>],
    "#channelA": [
        <ConnectionToUser1>,
        <ConnectionToUser3>
    ],
    "#channelB": [
        <ConnectionToUser1>,
        <ConnectionToUser2>
    ]
}
```

### `database.py`

服务器用来储存用户信息的数据库，使用 SQLite

默认数据库存放在当前目录下的 `users.db` 文件中

### `dbtool.py`

列出 `users.db` 中所有条目，展示数据库用

### `gui.py`

本来没有图形界面功能就已经很完善了，但其他组都在卷，功能做的花里胡哨。没个图形界面好像说不过去，没办法，给命令行套个壳子吧。

这个文件提供了两个借口，用来替换 `print` 和 `input` 函数

- `windows.terminal.printToTerminal(text: str)`

将文本打印在 GUI 上。

- `windows.getInput()`

获取用户输入的命令。如果用户没有输入，会阻塞直到用户输入

那么客户端如何使用 GUI 呢

在 `client.py` 开头有两句

```python
print = window.terminal.printToTerminal
input = window.getInput
```

这是将 python 默认的 `print` 函数和 `input` 函数替换成了 GUI 中的方法。client 其实完全可以不使用图形界面运作。
