from socket_manager.SocketClass import Socket
import socket
import json

class ServerSocket(Socket):
    
    def __init__(self, address_family: socket.AddressFamily, 
                 socket_type: socket.SocketKind) -> None:
        # creates socket, sets opts and gets ip
        super().__init__(address_family, socket_type)

        # port has to be allowed by firewall (linux)
        self.port: int = 8080
        self.socket.bind((self.ip, self.port))
        print(f"hosting at {self.ip}, listening to {self.port}. \nInitiating...")
        
        # other attributes
        self.player_no: int = 0
        self.ips: list[str] = [self.ip]
        self.ports: list[int] = [self.port]
        self.initiated: bool = False
    
    def connect_player(self) -> None:
        """
        Assign a player number to a connecting client.
        """
        _, client = self.socket.recvfrom(1024)
        print(f"Processing request from {client[0]}:{client[1]}")
        
        # compute player number
        self.ips.append(client[0])
        self.ports.append(client[1])
        client_player_number: bytes = json.dumps(len(self.ips)-1).encode()

        self.socket.sendto(client_player_number, client)
        self.socket.recvfrom(80)
        print(f"{client[0]}:{client[1]} connected.")
    
    def list_addresses(self) -> list[list[str | int]]:
        
        addresses: list[list[str | int]] = []
        # group addresses 
        for i in range(len(self.ips)):
            addresses.append([self.ips[i], self.ports[i]])
        return addresses

    def confirm_server_creation(self) -> None:
        """
        Confirms that all players are connected. If the message fails to be received,
        something went wrong.
        """
        self.initiated = True
        print("Sending confirmation to local clients.")
        
        addresses = self.list_addresses()
        self.assign_clients(addresses)
        addresses = json.dumps(addresses).encode()
        
        # send addresses to clients
        for index in range(1, len(self.ips)):
            self.socket.sendto(addresses, 
                               (self.ips[index], self.ports[index]))
        
        # this ensures that the clients reciprocate. May otherwise give error,
        # because the server runs to fast. Could be solved with tcp?
        confirmation, client = self.socket.recvfrom(80)
        confirmation, client = self.socket.recvfrom(80)
        
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
    sock: ServerSocket = ServerSocket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # enter feedback loop
    while not sock.initiated:
        # retrieve clients
        sock.connect_player()
        
        if len(sock.ips) == 3:
            sock.confirm_server_creation()
    return sock
