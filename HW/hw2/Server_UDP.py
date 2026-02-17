import socket

# Define IPs and Ports 
serverPort: int = 12000
serverHost: str = '127.0.0.1'

# Define socket for server
# UDP uses SOCK_DGRAM instead of SOCK_STREAM
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind socket to the corresponding IP and Port
serverSocket.bind((serverHost, serverPort))

print("The server is ready to receive")

# Receive data from the client
# recvfrom() blocks until data is received
# It returns (message, clientAddress) so we know where to send the reply
message, clientAddress = serverSocket.recvfrom(2048)
print('Received', message.decode())

# Send a response to the client
# We use sendto() and use the clientAddress we got from recvfrom()
response = 'Hello from server!'
serverSocket.sendto(response.encode(), clientAddress)

# Close the socket
serverSocket.close()
