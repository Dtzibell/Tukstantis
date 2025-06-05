import socket

class Socket(socket.socket):
    def __init__(self, address_family: socket.AddressFamily, 
                 socket_type: socket.SocketKind):
        super().__init__()
        self.socket = socket.socket(address_family, socket_type)
        # allows reusage of IP address (I think), otherwise kept getting OSError
        # if connected to server from terminal on same device
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip: str = self.get_ip()
        self.af = address_family
        self.sock_type = socket_type
    
    def get_ip(self) -> str:
        """
        this function connects the dgram socket to google,
        thus returns the router IP.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        s.close()
        return IP
    
    def assign_clients(self, addresses):
        """
        put address list into a clients attribute.
        """
        # deepcopy because list is later modified
       
        self.clients = addresses[:self.player_no] + addresses[self.player_no + 1:]
        for i in range(len(self.clients)):
            self.clients[i] = tuple(self.clients[i])
        print(f"Client list: {self.clients}")
