"""
    Sample code for Multi-Threaded Server
    Python 3
    Usage: python3 TCPserver3.py localhost 12000
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
from socket import *
from threading import Thread
import sys, select
import re 
import datetime
import logging

#####################################################################################################
# 
# Helper Functions 
#
#####################################################################################################

def message_response(valid_credentials, username, username_exists):
    if valid_credentials == True:
        reply_msg = 'Welcome to TESSENGER!'
        print('[send] ' + reply_msg)
    elif valid_credentials == False and username_exists == True: 
        reply_msg = "Invalid Password. Please try again"
        add_attempt = loginAttempts
        add_attempt[username] = 1 + add_attempt.get(username, 0)
        if add_attempt[username] == num_failed_consecutive_attempts:
            reply_msg = "Invalid Password. Your account has been blocked. Please try again later"

            blocked = blockedUser
            now = datetime.datetime.now()
            time_change = datetime.timedelta(seconds=10)
            new_time = now + time_change
            current_time = new_time.strftime("%d %b %Y %H:%M:%S")

            blocked[username] = current_time
    else: 
        reply_msg = "username does not exist in the database"
    return reply_msg


# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT ======\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

num_failed_consecutive_attempts = int(sys.argv[2])
if num_failed_consecutive_attempts < 1 or num_failed_consecutive_attempts > 5:
    print("Invalid number of allowed failed consecutive attempt: number. The valid value of argument number is an integer between 1 and 5")
    exit(0)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

loginAttempts = {}
blockedUser = {}

# Configure the first logger
logger1 = logging.getLogger('logger1')
logger1.setLevel(logging.INFO)

formatter1 = logging.Formatter('%(message)s')

file_handler1 = logging.FileHandler('userlog.txt')
file_handler1.setFormatter(formatter1)

logger1.addHandler(file_handler1)

# Configure the second logger
# logging.basicConfig(filename="messagelog.txt", level=logging.INFO, format='%(message)s')
logger2 = logging.getLogger('logger2')
logger2.setLevel(logging.INFO)

formatter = logging.Formatter('%(message)s')

file_handler = logging.FileHandler('messagelog.txt')
file_handler.setFormatter(formatter)

logger2.addHandler(file_handler)

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be ru ning in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    sequence_num = 0
    message_num = 0
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.clientlog = {}
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        message = ''
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            # handle message from the client
            if re.match(r'([^ ]+) ([^ ]+)', message) and len(message.split()) == 2: # message contains username and password
                print("[recv] New login request")
                self.process_login(message, clientAddress)
            elif message.startswith("UDP_PORT="):
                ClientThread.sequence_num += 1
                self.logUser(message, ClientThread.sequence_num, clientAddress)
            elif message.startswith("/msgto"): 
                if self.checkValidUser(message):
                    ClientThread.message_num += 1
                    info = self.logMessage(message, ClientThread.message_num)
                    message = f"{info[0]} {info[1]}"
                    self.clientSocket.send(message.encode())
                else: 
                    print("bad user")
            elif message.startswith("/activeuser"):
                if self.getActiveUsers(clientAddress) == []: 
                    message = "no other active user"
                    self.clientSocket.send(message.encode())
                else: 
                    for user in self.getActiveUsers(clientAddress): 
                        self.clientSocket.send(user.encode())
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self, message, client_address):
        username, password = re.split(' ', message)
        with open('credentials.txt', 'r') as file: 
            content = file.read()

        # check if user is blocked
        if username in blockedUser: 
            blocked = blockedUser[username] 
            date_format = "%d %b %Y %H:%M:%S"
            blocked_time = datetime.datetime.strptime(blocked, date_format)
            now = datetime.datetime.now()
            time_now = now.strftime(date_format)
            time_now = datetime.datetime.strptime(time_now, date_format)

            if blocked_time > time_now: # during blocked time
                reply_msg = "Your account is blocked due to multiple login failures. Please try again later"
            else: # after blocked time
                blockedUser.pop(username, None)
                loginAttempts[username] = 0
                valid_credentials = False 
                username_exists = False
                for row in re.split(r'\n', content):
                    valid_username, valid_password = re.split(r' ', row)
                    if username == valid_username and password == valid_password:
                        valid_credentials = True 
                        username_exists = True
                        break
                    if username == valid_username and password != valid_password:
                        valid_credentials = False
                        username_exists = True
                        break
                    
                    valid_credentials = False  
                    username_exists = False
                reply_msg = message_response(valid_credentials, username, username_exists)
        else: 
            valid_credentials = False 
            username_exists = False
            for row in re.split(r'\n', content):
                valid_username, valid_password = re.split(r' ', row)
                if username == valid_username and password == valid_password:
                    valid_credentials = True 
                    username_exists = True
                    self.clientlog[client_address] = {
                        'username': username,
                        'client_ip_address': client_address[0]
                    }
                    break

                if username == valid_username and password != valid_password:
                    valid_credentials = False
                    username_exists = True
                    break
                
                valid_credentials = False
                username_exists = False
                
            reply_msg = message_response(valid_credentials, username, username_exists)

        self.clientSocket.send(reply_msg.encode())

    def logUser(self, message, sequence_num, client_address):
        now = datetime.datetime.now()
        date_format = "%d %b %Y %H:%M:%S"
        time_now = now.strftime(date_format)

        if clientAddress in self.clientlog:
            user_info = self.clientlog[client_address]
            username = user_info['username']
            client_ip = user_info['client_ip_address']
            udp_port_number = re.split('=', message)[1]
            log_msg = f'{sequence_num};{time_now};{username}; {client_ip};{udp_port_number}'
            logger1.info(log_msg)
        else: 
            print(f"User not found for client {client_address}")

    def checkValidUser(self, message): 
        cmd = re.split(' ', message)[0]
        username = re.split(' ', message)[1]
        msg = re.split(' ', message)[2:]
        with open('credentials.txt', 'r') as file: 
            content = file.read()
        valid_user = False
        for row in re.split(r'\n', content):
            valid_username, valid_password = re.split(r' ', row)
            if username == valid_username: 
                valid_user = True
        return valid_user

    def logMessage(self, message, seq_num): 
        cmd = re.split(' ', message)[0]
        username = re.split(' ', message)[1]
        msg = ' '.join(re.split(' ', message)[2:])

        now = datetime.datetime.now()
        date_format = "%d %b %Y %H:%M:%S"
        time_now = now.strftime(date_format)
        log_msg = f'{seq_num};{time_now};{username};{msg}'
        logger2.info(log_msg)
        return [time_now, msg]

    def getActiveUsers(self, client_address):
        with open('userlog.txt', 'r') as file: 
            content = file.read()
        
        lst_active_users = []
        for row in re.split(r'\n', content):
            if len(row.split(';')) == 5: 
                user = re.split(';', row)[2]
                timestamp = re.split(';', row)[1]
                user_info = self.clientlog[client_address]
                username = user_info['username']
                if user == username: 
                    continue
                else: 
                    lst_active_users.append(f'{user}, active since {timestamp}')
        return lst_active_users

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()