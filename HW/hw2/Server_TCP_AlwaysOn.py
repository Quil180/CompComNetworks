import socket

# Define IPs and Ports
serverPort: int = 12000
serverHost: str = "127.0.0.1"

# Define sockets for server and client
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setting the socket to allow the reuse of addresses even after being used before.
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind socket to the corresponding IP and Port
serverSocket.bind((serverHost, serverPort))

# Waiting connection
serverSocket.listen(1)

try:
    while True:
        # Accept a connection with the client
        clientSocket, addr = serverSocket.accept()
        print(f"Connection was established with {addr}")

        # Receive data from the client
        data = clientSocket.recv(1024).decode()
        print(f"Received: {data}")

        # Send a response to the client
        message = "Hello from server!"
        if clientSocket.send(message.encode()) != len(message):
            print("Message sent was not correct amount of bytes/characters...")

        clientSocket.close()
        print("Client disconnected. Waiting for next connection...")

except KeyboardInterrupt:
    print("Server is shutting down...")

finally:
    # Close the service
    serverSocket.close()
