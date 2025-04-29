import socket

HOST = 'localhost'
PORT = 5050

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))  # corrected spelling + proper usage

while True:
    msg = input("You: ")
    client.send(msg.encode())

    if msg.lower() == "quit":
        break

    response = client.recv(1024).decode()
    print(f"Server: {response}")

client.close()
