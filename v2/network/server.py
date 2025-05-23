import socket
import threading

HOST = 'localhost'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}")

clients = []

def handle_client(conn, address):
    print(f"[NEW CONNECTION] {address} connected.")
    clients.append(conn)

    while True:
        try:
            message = conn.recv(1024)
            if not message:
                break
            broadcast(message, conn)
        except:
            break

    print(f"[DISCONNECT] {address} disconnected.")
    clients.remove(conn)
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
