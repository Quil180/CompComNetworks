import socket

# Define IPs and Ports 
clientPort: int = 12001
clientHost: str = '127.0.0.1'
serverPort: int = 12000
serverHost: str = '127.0.0.1'

# Define socket for client
# UDP uses SOCK_DGRAM instead of SOCK_STREAM
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind socket to the corresponding IP and Port
clientSocket.bind((clientHost, clientPort))

# Send data to the server
# UDP is connectionless, so we use sendto() with the destination address
# We do not use .connect()
message = 'Hello from client!'
clientSocket.sendto(message.encode(), (serverHost, serverPort))

# Receive data from the server
# recvfrom returns a tuple: (data, address)
data, serverAddress = clientSocket.recvfrom(2048)
print('Received', data.decode())

# Close the socket
clientSocket.close()
