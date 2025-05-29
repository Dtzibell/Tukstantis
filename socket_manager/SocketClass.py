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

    def convert_list_to_bytes(self, to_send, separators: list = ["/", "::", ":"], recursion_level = 0):
        """
        converts a list to a string with predefined separators or nested lists.
        
        the separators list has to be the most specific at the top level -
        for example, :: has to be higher up than :
        """
        for index, item in enumerate(to_send):
            if isinstance(item, list):
                to_send[index] = self.convert_list_to_bytes(item, separators[1:], recursion_level+1)
            elif not isinstance(item, str):
                to_send[index] = str(item)
        to_send = separators[0].join(to_send)
        # converts to bytes if at top recursion level
        if recursion_level == 0:
            to_send = to_send.encode()
        return to_send
    
    def convert_bytes_to_list(self, received, separators: list = ["/", "::", ":"]):
        """
        converts bytes to a list based ond predefined separators to denote nested lists.
        """
        if type(received) == bytes:
            received = received.decode()
        received = received.split(separators[0])
        for index in range(len(received)):
            if received[index].isdigit():
                received[index] = int(received[index])
            elif separators[1] in received[index]:
                received[index] = self.convert_bytes_to_list(received[index], separators[1:])
        return received

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
