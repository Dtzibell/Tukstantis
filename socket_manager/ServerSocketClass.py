import socket
import sys
from collections import defaultdict
import time
from copy import deepcopy

def get_ip() -> str:
        """
        this function connects the dgram socket to google,
        thus returns the router IP.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        s.close()
        return IP

class ServerSocket(socket.socket):
    
    
    def __init__(self, address_family: socket.AddressFamily, 
                 socket_type: socket.SocketType):
        
        super().__init__()
        # create socket
        self.socket = socket.socket(address_family, socket_type)
        # allows reusage of IP address (I think), otherwise kept getting OSError
        # if connected to server from terminal on same device
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip: str = get_ip()
        # port has to be allowed by firewall (linux)
        self.port = 8080
        self.socket.bind((self.ip, self.port))
        print(f"created the server at {self.ip}, listening to {self.port}. \nInitiating...")
        
        # other attributes
        self.player_no = 0
        self.ips = [self.ip]
        self.ports = [self.port]
        self.initiated = False
    
    def get_client(self):
        """
        Receives from client and sends the player number of the client.
        """
        _, sender = self.socket.recvfrom(1024)
        print(f"Processing request from {sender[0]}:{sender[1]}")
        
        # TODO: not sure if ips and ports lists are useful, could probably
        # replace with separate count attribute within the server class
        self.ips.append(sender[0])
        self.ports.append(sender[1])
        player_number = (len(self.ips) - 1).to_bytes()

        self.socket.sendto(player_number, sender)
        print(f"{sender[0]}:{sender[1]} connected.")
    
    def make_address_list(self):
        address_list = []
        for i in range(len(self.ips)):
            address_list.append([self.ips[i], self.ports[i]])
        self.clients = deepcopy(address_list[1:])
        for i in range(len(self.clients)):
            self.clients[i] = tuple(self.clients[i])
        print(f"Player list: {self.clients}")
        return address_list
    
    def convert_addresses_to_bytes(self, address_list:list[str,int]):
        for i, address in enumerate(address_list):
            address_list[i][1] = str(address[1])
            address_list[i] = ":".join(address)
        address_list = "/".join(address_list)
        return address_list

    def confirm_server_creation(self):
        """
        Confirms that all players are connected. If the message fails to be received,
        something went wrong.
        """
        self.initiated = True
        print("Sending confirmation to local clients.")
        
        address_list = self.make_address_list()
        
        address_list = self.convert_addresses_to_bytes(address_list)
        
        # send addresses to clients
        for index in range(1, len(self.ips)):
            self.socket.sendto(bytes(address_list, "utf-8"), 
                               (self.ips[index], self.ports[index]))
        
        # this ensures that the clients reciprocate. May otherwise give error,
        # because the server runs to fast. Could be solved with tcp?
        msg, server = self.socket.recvfrom(80)
        msg, server = self.socket.recvfrom(80)
        
        for index in range(1, len(self.ips)):
            self.socket.sendto(b"The server was successfully initiated", 
                                (self.ips[index], self.ports[index]))
        print("The server was successfully initiated.")

def initiate_server() -> ServerSocket:
    """
    creates the socket, accepts clients and sends out confirmations.
    returns the server socket
    """
    # create server socket
    sock = ServerSocket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # enter feedback loop
    while not sock.initiated:
        # retrieve clients
        sock.get_client()
        
        if len(sock.ips) == 3:
            sock.confirm_server_creation()
    return sock

