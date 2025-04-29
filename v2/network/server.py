import socket

HOST = 'localhost'  # or your LAN IP like '192.168.1.5'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"[SERVER] Listening on {HOST}:{PORT}...")
conn, addr = server.accept()
print(f"[SERVER] Connected by {addr}")

while True:
    data = conn.recv(1024).decode()
    if data == "quit":
        print("[SERVER] Client disconnected.")
        break
    print(f"[CLIENT] {data}")
    conn.send("Got it!".encode())

conn.close()
