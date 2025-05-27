import socket
from socket_manager.ServerSocketClass import get_ip

class ClientSocket(socket.socket):
    def __init__(self, address_family: socket.AddressFamily, 
                 socket_type: socket.SocketType):
        self.socket = socket.socket(address_family, socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # af, type and ip are needed for later replacement of socket
        self.af = address_family
        self.sock_type = socket_type

        # get_ip unfortunately does not define the port
        self.ip = get_ip()

        self.initiated:bool = False
    
    def get_player_no(self, player_number:str) -> int:
        """
        defines the port and receives the player number of the socket from the server
        """
        # msg is the player number
        self.player_no = int.from_bytes(player_number)
        # port was defined by sendto, can now be called 
        self.port = self.socket.getsockname()[1]
        self.socket.close()
        return self.port
    
    def set_clients(self, addresses:str):
        """
        post-processes addresses and places them in a list.
        addresses has to be in the form IP:PORT/IP:PORT...
        """
        addresses: str = addresses.decode()

        addresses: list[str] = addresses.split("/")
        for i, address in enumerate(addresses):
            addresses[i] = address.split(":")
            addresses[i][1] = int(addresses[i][1])
            addresses[i] = tuple(addresses[i])

        self.clients:list[str,int] = addresses[:self.player_no] + addresses[self.player_no + 1:]
        print(f"Client list: {self.clients}")


    def become_client(self, SERVER_IP: str):
        """
        connects with the server on the basis of reciprocity
        this way collects the player number and the address list
        """
        # receives the player number from the server
        self.socket.sendto(b"Connection", (SERVER_IP, 8080))
        str_player_number, _ = self.socket.recvfrom(1024)
        self.port = self.get_player_no(str_player_number)
        
        # since socket sends to local network, its IP is set to 0.0.0.0
        # this however does not suit my purpose, need to replace the socket
        self.socket = socket.socket(self.af, self.sock_type)
        self.socket.bind((self.ip,self.port))
        print(f"Socket created at {self.ip}:{self.port}")
        
        # receives the addresses from the server
        addresses, _ = self.socket.recvfrom(1024)
        self.set_clients(addresses)
        self.socket.sendto(b"", (SERVER_IP, 8080))
        
        # receives final confirmation
        msg, _ = self.socket.recvfrom(80)
        msg = msg.decode()
        assert msg == "The server was successfully initiated"
        print("Connection established.")
        self.initiated = True
    
def initiate_client(SERVER_IP: str) -> ClientSocket:
    """
    creates a feedback loop with the server and returns the 
    ClientSocket associated with the device
    """
    sock = ClientSocket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while not sock.initiated:
        sock.become_client(SERVER_IP)

    return sock

if __name__ == "__main__":
    print(socket.AF_INET)

"""
for the future:
- can maybe implement a reconnection feature? or an autosave function and 
a load from file function? many ideas to expand there, as connection may be lost mid
game.
"""