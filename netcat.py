import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

# here we set up the functionality for the -e or --execute command
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),
                                     stderr=subprocess.STDOUT)
    return output.decode()

# here we create the NetCat class that takes arguments from the command line and
# creates a socket object
class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# this function delegates execution to either the listen function or the send function
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
# this function provides functionality for the send method
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

# this function provides functionality for the listen method
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()
# this function create a handler for when a connection is established
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()
# this if statement provides the infomation in the --help menu
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'BHP Net Tool',
    formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''
    Example:
    netcat.py -t 192.168.1.108 -p 5555 -1 -c #command shell
    netcat.py -t 192.168.1.108 -p 5555 -1 -u=mytest.txt #upload a file
    netcat.py -t 192.168.1.108 -p 5555 -1 -e=\"cat /etc/passwd\" #execute command
    echo "ABC" | ./necat.py -t 192.168.1.108 -p 555 #echo text to port
    netcat.py -t 192.168.1.108 -p 5555 #connect to a server'''))
parser.add_argument('-c', '--command', action='store_true', help='command shell')
parser.add_argument('-e', '--execute', help='execute a command')
parser.add_argument('-l', '--listen', action='store_true',help='listen to a port')
parser.add_argument('-p', '--port', type=int, default=5555, help='specify port number')
parser.add_argument('-t', '--target', default='192.168.1.108', help='specified target IP')
parser.add_argument('-u', '--upload', help='upload file')
args = parser.parse_args()
if args.listen:
    buffer = ''
else:
    buffer = sys.stdin.read()

nc = NetCat(args, buffer.encode())
nc.run()
