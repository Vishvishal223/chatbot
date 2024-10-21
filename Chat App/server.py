import socket
import threading
import time

PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
HISTORY_FILE = "chat_history.txt"
clients = {}
names = {}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def startChat():
    print("Server is running on " + SERVER)
    server.listen()

    while True:
        conn, addr = server.accept()
        conn.send("NAME".encode(FORMAT))

        name = conn.recv(1024).decode(FORMAT)
        if name in names.values():
            conn.send("NAME_TAKEN".encode(FORMAT))
            conn.close()
            continue

        names[conn] = name
        clients[name] = conn
        print(f"Name is :{name}")
        broadcastMessage(f"{name} has joined the chat!\n".encode(FORMAT))
        conn.send('Connection successful!'.encode(FORMAT))

        thread = threading.Thread(target=handle, args=(conn, addr))
        thread.daemon = True
        thread.start()

        print(f"Active connections {threading.activeCount() - 1}")

def handle(conn, addr):
    name = names[conn]
    while True:
        try:
            message = conn.recv(1024).decode(FORMAT)
            if not message:
                break
            if message.startswith('/msg'):
                parts = message.split(maxsplit=2)
                if len(parts) < 3:
                    conn.send("Invalid private message format. Use /msg <username> <message>".encode(FORMAT))
                    continue
                _, recipient, private_message = parts
                if recipient in clients:
                    clients[recipient].send(f"\nPrivate message from {name}: {private_message}\n".encode(FORMAT))
                else:
                    conn.send("User not found.".encode(FORMAT))
            elif message.startswith('/status'):
                _, status = message.split(maxsplit=1)
                broadcastMessage(f"\n{name} is now {status}\n".encode(FORMAT))
            else:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                full_message = f"{timestamp}\n{name}: {message}\n"  # Ensure newline after timestamp and before message
                broadcastMessage(full_message.encode(FORMAT))
                saveChatHistory(full_message)
        except:
            conn.close()
            del names[conn]
            del clients[name]
            broadcastMessage(f"\n{name} has left the chat.\n".encode(FORMAT))
            break

def broadcastMessage(message):
    for client in clients.values():
        client.send(message)

def saveChatHistory(message):
    with open(HISTORY_FILE, "a") as file:
        file.write(message + "\n")

startChat()
