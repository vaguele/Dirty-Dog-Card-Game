import socket
import threading

HOST = 'localhost'
PORT = 5050

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            print(f"\n[RECEIVED] {msg}")
        except:
            print("[ERROR] Disconnected from server.")
            client.close()
            break

def send():
    while True:
        msg = input("You: ")
        client.send(msg.encode())

# Start threads
threading.Thread(target=receive, daemon=True).start()
send()
