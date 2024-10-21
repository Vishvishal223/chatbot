import socket
import threading
from tkinter import *
from datetime import datetime

PORT = 5000
SERVER = "192.168.6.35"  # Replace with the server's IP address
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

class GUI:
    def __init__(self):
        self.Window = Tk()
        self.Window.withdraw()
        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)
        self.pls = Label(self.login, text="Please login to continue", justify=CENTER, font="Helvetica 14 bold")
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")
        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)
        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)
        self.entryName.focus()
        self.go = Button(self.login, text="CONTINUE", font="Helvetica 14 bold", command=lambda: self.goAhead(self.entryName.get()))
        self.go.place(relx=0.4, rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name):
        client.send(name.encode(FORMAT))
        response = client.recv(1024).decode(FORMAT)
        if response == 'NAME_TAKEN':
            print("Name already taken. Try another.")
            self.login.destroy()
            self.__init__()
            return
        self.login.destroy()
        self.layout(name)
        rcv = threading.Thread(target=self.receive)
        rcv.daemon = True
        rcv.start()

    def layout(self, name):
        self.name = name
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")
        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window, width=450, bg="#ABB2B9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)
        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)
        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)
        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.entryMsg.focus()
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9", command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        self.textCons.config(cursor="arrow")
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)

    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.sendMessage)
        snd.daemon = True
        snd.start()

    def receive(self):
        while True:
            try:
                message = client.recv(1024).decode(FORMAT)
                if not message:
                    break
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, message)  # No extra newline is added here; message already formatted
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
            except Exception as e:
                print(f"An error occurred: {e}")
                client.close()
                break

    def sendMessage(self):
        print(f"Sending message: {self.msg}")  # Debugging statement
        if self.msg.startswith('/status'):
            client.send(self.msg.encode(FORMAT))
        elif self.msg.startswith('/msg'):
            client.send(self.msg.encode(FORMAT))
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{timestamp}\n{self.name}: {self.msg}\n"  # Ensure newline between timestamp and message
            client.send(message.encode(FORMAT))

g = GUI()