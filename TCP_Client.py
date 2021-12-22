import socket

target_host = 'www.google.com'
target_port = 80

# create a socket object
# socket.AF_NET means that the socket we are creating is going to be an IPv4 address
# socket.SOCK_STREAM means that we are creating a TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the client
client.connect((target_host, target_port))

# sending some data
client.send(b"GET / HTTP/ 1.1\r\nHost: google.come\r\n\r\n")

# recieve some data
response = client.recv(4096)

# print the response
print(response.decode())

# close the connection
client.close()
