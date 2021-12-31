import tkinter
import queue


class Terminal:
    def __init__(self, master):
        self.master = master
        self.frame = tkinter.Frame(master)
        self.frame.pack()
        self.verticalScrollbar = tkinter.Scrollbar(
            self.frame, orient=tkinter.VERTICAL)
        self.text = tkinter.Text(
            self.frame, yscrollcommand=self.verticalScrollbar.set)
        self.verticalScrollbar.config(command=self.text.yview)
        self.verticalScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.text.pack()
        self.text.insert(tkinter.END, "Welcome to the terminal!\n")
        self.text.config(state=tkinter.DISABLED)
        self.text.config(font=("Courier", 12))
        # self.text.config(background="black", foreground="white")
        # self.text.config(insertbackground="white")
        # self.text.config(selectbackground="black", selectforeground="white")
        self.text.config(cursor="arrow")
        self.text.config(wrap=tkinter.WORD)
        self.text.config(padx=5, pady=5)
        self.text.config(undo=True)
        self.text.config(autoseparators=True)
        self.text.config(spacing1=5, spacing2=5, spacing3=5)
        self.text.config(tabs=5)
        self.text.config(width=80)
        self.text.config(height=10)
        self.text.config(state=tkinter.DISABLED)
        self.text.config(font=("Monospace", 12))

    def printToTerminal(self, text):
        self.text.config(state=tkinter.NORMAL)
        for line in text.splitlines():
            self.write(line + "\n")
        self.text.config(state=tkinter.DISABLED)

    def write(self, text):
        self.text.config(state=tkinter.NORMAL)
        self.text.insert(tkinter.END, text)
        self.text.config(state=tkinter.DISABLED)
        self.text.see(tkinter.END)
        # set verticalScrollbar to button position
        self.verticalScrollbar.set(1.0, 1.0)

    def clear(self):
        self.text.config(state=tkinter.NORMAL)
        self.text.delete(1.0, tkinter.END)
        self.text.config(state=tkinter.DISABLED)


class Window(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("IRC Client")
        # self.geometry("800x600")
        # self.resizable(False, False)
        self.terminal = Terminal(self)
        self.controlFrame = tkinter.Frame(self)
        self.inputEntry = tkinter.Entry(
            self.controlFrame, font=("Courier", 12), width=50)
        self.inputEntry.pack(side=tkinter.LEFT)
        self.sendButton = tkinter.Button(
            self.controlFrame, text="Send", command=self.send, font=("Courier", 12))
        self.sendButton.pack(side=tkinter.LEFT)
        self.clearButton = tkinter.Button(
            self.controlFrame, text="Clear", command=self.terminal.clear, font=("Courier", 12))
        self.clearButton.pack(side=tkinter.LEFT)
        self.controlFrame.pack(side=tkinter.BOTTOM)
        self.inputEntry.bind("<Return>", lambda event: self.send())
        self.inputQueue = queue.Queue()

    def send(self):
        self.inputQueue.put(self.inputEntry.get())
        self.inputEntry.delete(0, tkinter.END)

    def write(self, text):
        self.terminal.write(text)

    def getInput(self, arg=""):
        if arg:
            self.terminal.printToTerminal(arg)

        return self.inputQueue.get()


window = Window()
