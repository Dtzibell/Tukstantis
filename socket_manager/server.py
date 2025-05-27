# first of all import the socket library 
from socket_manager.ClientSocketClass import initiate_client
from socket_manager.ServerSocketClass import initiate_server

def run_server():

    # get socket type
    socket_purpose = input("Would you like to create a server or connect? [server/connect]: ")

    if socket_purpose == "server":
        sock = initiate_server()
    elif socket_purpose == "connect":
        # SERVER_IP = input("Enter IP: ")
        SERVER_IP = "192.168.178.162"
        sock = initiate_client(SERVER_IP)

    return sock, socket_purpose