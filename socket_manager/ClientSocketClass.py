import socket
from socket_manager.SocketClass import Socket
import json

class ClientSocket(Socket):
    def __init__(self, address_family: socket.AddressFamily, 
                 socket_type: socket.SocketKind) -> None:
        super().__init__(address_family, socket_type)
        # af, type and ip are needed for later replacement of socket
        self.initiated: bool = False
    
    def become_client(self, SERVER_IP: str) -> None:
        """
        connects with the server on the basis of reciprocity
        this way collects the player number and the address list
        """
        # receives the player number from the server
        self.socket.sendto(b"Connection", (SERVER_IP, 8080))
        player_number_bytes, _ = self.socket.recvfrom(1024)
        self.player_no: int = json.loads(player_number_bytes)
        self.port: int = self.socket.getsockname()[1]
        
        # since socket sends to local network, its IP is set to 0.0.0.0
        # this however does not suit my purpose, need to replace the socket
        self.socket: socket.socket = socket.socket(self.af, self.sock_type)
        self.socket.bind((self.ip,self.port))
        print(f"Socket created at {self.ip}:{self.port}")
        self.socket.sendto(b"", (SERVER_IP, 8080))
        
        # receives the addresses from the server
        addresses_bytes, _ = self.socket.recvfrom(1024)
        addresses: list[str | int] = json.loads(addresses_bytes)
        self.assign_clients(addresses)
        self.socket.sendto(b"", (SERVER_IP, 8080))
        
        # receives final confirmation
        msg, _ = self.socket.recvfrom(80)
        assert msg == b"The server was successfully initiated"
        print("Connection established.")
        self.initiated: bool = True
    
def initiate_client(SERVER_IP: str) -> ClientSocket:
    """
    creates a feedback loop with the server and returns the 
    ClientSocket associated with the device
    """
    sock: ClientSocket = ClientSocket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while not sock.initiated:
        sock.become_client(SERVER_IP)

    return sock


