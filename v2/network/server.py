import socket
import threading

HOST = 'localhost'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}")

clients = []

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    # sends a message from the server to the client 
    # encode() converts string to bytes
    conn.send("Welcome! Please type 'JOIN <name>' to enter the game.".encode())

    clients.append(conn)
    player_name = None

    while True:
        try:
            # decode converts bytes to string
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break

            if msg.startswith("JOIN "):
                player_name = msg[5:].strip()
                print(f"[JOIN] {player_name} joined from {addr}")
                conn.send(f"Hello, {player_name}! You joined the game.".encode())
                broadcast(f"{player_name} has joined the game.".encode(), conn)

            elif msg.startswith("SAY "):
                if player_name:
                    chat_msg = msg[4:].strip()
                    print(f"[{player_name}] says: {chat_msg}")
                    broadcast(f"{player_name}: {chat_msg}".encode(), conn)
                else:
                    conn.send("You must JOIN before sending messages.".encode())

            else:
                conn.send("Unknown command. Use 'JOIN <name>' or 'SAY <message>'.".encode())

        except:
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    clients.remove(conn)
    if player_name:
        broadcast(f"{player_name} has left the game.".encode(), conn)
    conn.close()

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            client.send(message)

def start():
    while True:
        conn, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, address))
        thread.start()

start()
