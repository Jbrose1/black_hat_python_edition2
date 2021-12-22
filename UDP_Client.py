import socket

target_host = "127.0.0.1"
target_port = 9997

# create a client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b"AAABBBCCC", (target_host, target_port))

# recieve data
data, addr = client.recvfrom(4096)

# print the data
print(data.decode())

# close client
client.close()
