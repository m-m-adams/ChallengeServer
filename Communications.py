import socket


class Server:
    def __init__(self, bind_address, bind_port):
        # Create the socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set socket options
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)

        # Bind the socket
        self.s.bind((bind_address, bind_port))

        # Set number of listeners
        self.s.listen(50)



    def accept_connection(self):
        # Block until connection accepted
        client_s, client_addr = self.s.accept()

        #give the client socket a timeout
        client_s.settimeout(30)
        # Create a client communication interface
        client_interface = Client(client_s, client_addr)

        # Return the client communication interface
        return client_interface


class Client:
    READ_SIZE = 2048

    def __init__(self, client_socket, client_address):
        # Store client socket
        self.client_s = client_socket

        # Store client address
        self.client_addr = client_address

    def send(self, byte_message):
        # Send message to client
        self.client_s.sendall(byte_message)

    def recv(self):
        # Recv message from client
        return self.client_s.recv(self.READ_SIZE)

    def get_addr(self):
        # Return the stored address
        return self.client_addr

    def get_socket(self):
        # Return the stored socket
        return self.client_s
