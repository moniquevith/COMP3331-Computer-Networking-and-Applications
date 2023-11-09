"""
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
from socket import *
import sys
import re
import threading
import time

#Server would be running on the same host as Client
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)

# Create a UDP socket and bind it to an available port
udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind(('0.0.0.0', 0))  # Binding to port 0 to let the OS choose a port

# Get the actual port number that the OS assigned
local_address = udp_socket.getsockname()
udp_port_number = local_address[1]

exit_client = False

def recv_handler():
    global exit_client
    while True:
        data = clientSocket.recv(1024)
        receivedMessage = data.decode()
        if receivedMessage.startswith("Bye,"):
            print(receivedMessage)

            # close the socket
            clientSocket.close()
            udp_socket.close()

            exit_client = True
            break
        else:
            print(receivedMessage)

def send_handler():
    global exit_client
    while True: 
        command = input("Enter one of the following commands (/msgto, /activeuser, /creategroup, /joingroup, /groupmsg, /logout):")
        if command.startswith('/msgto'):
            if len(command.split()) < 3: 
                print("Invalid use of command /msgto")                  
            else: 
                cmd = re.split(' ', command)[0]
                username = re.split(' ', command)[1]
                msg = ' '.join(re.split(' ', command)[2:])
                if msg.isspace():
                    print("Invalid use of command /msgto")
                    continue
                else: 
                    message = f'{cmd} {username} {msg}'
                    clientSocket.send(message.encode())
        if command.startswith('/activeuser'):
            message = '/activeuser'
            clientSocket.send(message.encode())
        if command.startswith('/creategroup'): 
            if len(command.split()) < 3: 
                print("Invalid use of command /creategroup") 
                continue              
            else: 
                message = command
                clientSocket.send(message.encode())
        if command.startswith('/joingroup'):
            if len(command.split()) < 2: 
                    print("Invalid use of command /joingroup")
                    continue
            else: 
                message = command
                clientSocket.send(message.encode())
        if command.startswith('/groupmsg'):
            if len(command.split()) < 3: 
                    print("Invalid use of command /groupmsg")
                    continue
            else: 
                message = command
                clientSocket.send(message.encode())
        if command.startswith('/logout'):
            message = '/logout'
            clientSocket.send(message.encode())
            exit_client = True
            break

def run_threads():
    recv_thread = threading.Thread(target=recv_handler)
    recv_thread.daemon = True
    recv_thread.start()

    sending_thread = threading.Thread(target=send_handler)
    sending_thread.daemon = True
    sending_thread.start()

    while True:
        time.sleep(0.1)

        if exit_client:
            exit(0)

def log_in(retry_password, logged_in, curr_user):
    if retry_password: 
        password = input("Password: ")
        message = f'{curr_user} {password}'
        clientSocket.sendall(message.encode())
    else: 
        print("Please Login")
        username = input("Username: ")
        password = input("Password: ")
        curr_user = username
        message = f'{username} {password}'
        clientSocket.sendall(message.encode())

    # receive response from the server
    # 1024 is a suggested packet size, you can specify it as 2048 or others
    data = clientSocket.recv(1024)
    receivedMessage = data.decode()

    if receivedMessage == "":
        print("[recv] Message from server is empty!")
    elif receivedMessage == "Welcome to TESSENGER!":
        print(receivedMessage)
        udp_port = 'UDP_PORT=' + str(udp_port_number)
        clientSocket.send(udp_port.encode())
        run_threads()
    elif receivedMessage == "Invalid Password. Please try again":
        print(receivedMessage)
        logged_in = False
        retry_password = True
        log_in(retry_password, logged_in, curr_user)
    elif receivedMessage == "username does not exist in the database":
        print(receivedMessage)
        logged_in = False
        retry_password = False
        log_in(retry_password, logged_in, curr_user)
    elif receivedMessage == "Invalid Password. Your account has been blocked. Please try again later":
        print(receivedMessage)


if __name__ == "__main__":
    # start to authenticate user
    retry_password = False
    logged_in = False
    curr_user = ''
    log_in(retry_password, logged_in, curr_user)