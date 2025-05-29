# first of all import the socket library 
from socket_manager.ClientSocketClass import initiate_client
from socket_manager.ServerSocketClass import initiate_server

def run_server():

    # get socket type
    socket_purpose = input("Are you a host or a client? [host/client]: ")

    if socket_purpose == "host":
        sock = initiate_server()
    elif socket_purpose == "client":
        # SERVER_IP = input("Enter IP: ")
        SERVER_IP = "192.168.178.162"
        sock = initiate_client(SERVER_IP)

    return sock, socket_purpose
