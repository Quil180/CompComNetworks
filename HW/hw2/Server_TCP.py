import socket

# Define IPs and Ports
serverPort = 12000
serverHost = "127.0.0.1"

# Define sockets for server and client
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to the corresponding IP and Port
serverSocket.bind((serverHost, serverPort))

# Waiting connection
serverSocket.listen(1)

# Accept a connection with the client
clientSocket = serverSocket.accept()[0]

# Receive data from the client
data = clientSocket.recv(1024).decode()
print("Received", data)

# Send a response to the client
message = "Hello from server!"
if clientSocket.send(message.encode()) != len(message):
    print(f"Message sent had error and could not send all {len(message)} characters...")

# Close the connection
clientSocket.close()

# Close the service
serverSocket.close()
