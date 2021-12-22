import socket
import threading

# Here we are listing an IP and a Port that our server will be listning on
IP = "0.0.0.0"
PORT = 9998

# below is where the server will begin to listen. We will first set the server
# up as a TCP server. Then we will bind the server to the IP and PORT Variables.
# Next, we will set the max backlog connections to 5.
# Finally, the code will print what IP and port it is listening on.
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f"[*] Listen on {IP}:{PORT}")

# The while loop is used to run code while the client is connected to the server.
# First, the information from server.accpet() will be stored in client and address Variables.
# Once the user is connected the code will print the connection details to the terminal.
# Next, the code will establish a client handler.
# Finally, the code will start up the client handler.

    while True:
        client, address = server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Recieved: {request.decode("utf-8")}')
        sock.send(b"ACK")

if __name__ == "__main__":
    main()
