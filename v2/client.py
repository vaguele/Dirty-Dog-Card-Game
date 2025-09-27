import socket
import threading

HOST = 'localhost'
PORT = 5050

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            # Read a larger buffer and normalize whitespace so server-leading newlines
            # don't produce double blank lines on the client terminal.
            msg = client.recv(4096).decode()
            if msg:
                # Strip leading/trailing whitespace/newlines then print with a single
                # leading newline for consistent spacing.
                normalized = msg.strip()
                if normalized:
                    print(f"\n{normalized}")
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
            msg = input("")
            if msg.lower() == "quit":
                break
            client.send(f"{msg}".encode())  
        except:
            break
    client.close()

# Start threads
threading.Thread(target=receive, daemon=True).start()
send()
