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

def doCommand(): 
    while True: 
        command = input("Enter one of the following commands (/msgto, /activeuser, /creategroup, /joingroup, /groupmsg, /logout):")
        if command.startswith('/msgto'):
            parts = command.split()
            if len(parts) < 3: 
                print("Invalid use of command /msgto")
                continue
            else: 
                cmd = re.split(' ', command)[0]
                username = re.split(' ', command)[1]
                msg = ' '.join(re.split(' ', command)[2:])
                if msg.isspace():
                    print("Invalid use of command /msgto")
                    continue
                else: 
                    return f'{cmd} {username} {msg}'
        if command.startswith('/activeuser'):
            return '/activeuser'
        if command.startswith('/creategroup'): 
            if len(command.split()) < 3: 
                print("Invalid use of command /creategroup")
                continue
            else: 
                return command
        if command.startswith('/joingroup'):
            if len(command.split()) < 2: 
                    print("Invalid use of command /joingroup")
                    continue
            else: 
                return command
        if command.startswith('/groupmsg'):
            if len(command.split()) < 3: 
                    print("Invalid use of command /groupmsg")
                    continue
            else: 
                return command

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


# Function for user input and printing received messages
def user_interaction():
    while True:
        user_input = input("Enter a message to send to the server (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        clientSocket.send(user_input.encode())

        server_response = clientSocket.recv(1024).decode()
        print(f"Server says: {server_response}")

# Function to continuously listen for incoming messages from the server and print them
def receive_messages():
    while True:
        server_message = clientSocket.recv(1024).decode()
        print(f"Received 2 from server: {server_message}")

# Create and start the user interaction thread
user_thread = threading.Thread(target=user_interaction)
user_thread.start()

# Create and start the receive messages thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Wait for both threads to complete
user_thread.join()
receive_thread.join()

# Close the socket after both threads exit
clientSocket.close()