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
            if msg:
                print(f"\n{msg}")
            else:
                break
        except:
            print("[ERROR] Disconnected from server.")
            client.close()
            break

def send():
    name = input("Enter your name: ")

    # Send JOIN command on connection
    client.send(f"{name}".encode())  

    while True:
        try:
            msg = input("You: ")
            if msg.lower() == "quit":
                break
            client.send(f"{msg}".encode())  
        except:
            break
    client.close()

# Start threads
threading.Thread(target=receive, daemon=True).start()
send()
