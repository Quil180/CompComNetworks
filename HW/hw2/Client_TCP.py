import socket

# Define IPs and Ports
clientPort = 12001
clientHost = "127.0.0.2"
serverPort = 12000
serverHost = "127.0.0.1"

# Define sockets for server and client
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to the corresponding IP and Port
clientSocket.bind((clientHost, clientPort))

# Connect to the server
clientSocket.connect((serverHost, serverPort))

# Send data to the server
message = "Hello from client!"
if clientSocket.send(message.encode()) != len(message):
    print(f"Message sent had error and could not send all {len(message)} characters...")

# Receive data from the server
data = clientSocket.recv(1024)
print("Received", data.decode())

# Close the connection
clientSocket.close()
