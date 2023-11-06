"""
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
from socket import *
import sys
import re

def doCommand(): 
    while True: 
        command = input("Enter one of the following commands (/msgto, /activeuser, /creategroup, /joingroup, /groupmsg, /logout):")
        if command.startswith('/msgto'):
            parts = command.split()
            if len(parts) < 3: 
                print("Invalid use of command /msgto, please follow this format /msgto USERNAME MESSAGE_CONTENT and try again.")
                continue
            else: 
                cmd = re.split(' ', command)[0]
                username = re.split(' ', command)[1]
                msg = ' '.join(re.split(' ', command)[2:])
                if msg.isspace():
                    print("Invalid use of command /msgto, please follow this format /msgto USERNAME MESSAGE_CONTENT and try again.")
                    continue
                else: 
                    return f'{cmd} {username} {msg}'
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

retry_password = False
curr_user = ''
while True:
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

    # parse the message received from server and take corresponding actions
    if receivedMessage == "":
        print("[recv] Message from server is empty!")
    elif receivedMessage == "Welcome to TESSENGER!":
        print(receivedMessage)
        retry_password = False
        udp_port = 'UDP_PORT=' + str(udp_port_number)
        clientSocket.send(udp_port.encode())
        clientSocket.send(doCommand().encode())
    elif receivedMessage == "Invalid Password. Please try again":
        print(receivedMessage)
        retry_password = True
        continue
    elif receivedMessage == "username does not exist in the database":
        print(receivedMessage)
        retry_password = False
        continue
    elif receivedMessage == "Invalid Password. Your account has been blocked. Please try again later":
        print(receivedMessage)
        break
    elif receivedMessage == "download filename":
        print("[recv] You need to provide the file name you want to download")
    else:
        print(receivedMessage)
        
    ans = input('\nDo you want to continue(y/n) :')
    if ans == 'y':
        continue
    else:
        break

# close the socket
clientSocket.close()
udp_socket.close()