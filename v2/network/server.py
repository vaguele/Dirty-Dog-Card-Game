import socket
import threading

HOST = 'localhost'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}")

clients = []
players = {}  # conn: {"name": str}
MIN_PLAYERS = 3
game_started = False

def handle_client(conn, addr):
    global game_started

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
            
            # JOIN command
            if msg.startswith("JOIN "):
                player_name = msg[5:].strip()
                players[conn] = {"name": player_name}
                print(f"[JOIN] {player_name} joined from {addr}")
                conn.send(f"Hello, {player_name}! You joined the game.".encode())
                conn.send(f"\nWaiting for other players...".encode())
                broadcast(f"{player_name} has joined the game.".encode(), conn)

                # Start game when enough players join
                if not game_started and len(players) >= MIN_PLAYERS:
                    broadcast("GAME START".encode(), None)
                    game_started = True
                continue

            # SAY command
            elif msg:
                if player_name:
                    chat_msg = msg.strip()
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
