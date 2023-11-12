def send_file(file_path, destination_ip, destination_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(file_path, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break

            udp_socket.sendto(data, (destination_ip, destination_port))

    udp_socket.close()

def receive_file(save_path, listening_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", listening_port))

    with open(save_path, 'wb') as file:
        while True:
            data, addr = udp_socket.recvfrom(1024)
            if not data:
                break

            file.write(data)

    udp_socket.close()

# Example usage for sending a file
file_to_send = "path/to/your/file.txt"
receiver_ip = "127.0.0.1"  # Replace with the IP address of the receiving client
receiver_port = 12345  # Replace with the port number of the receiving client

send_file(file_to_send, receiver_ip, receiver_port)

# Example usage for receiving a file
save_received_file = "path/to/save/received/file.txt"
sender_port = 12345  # Choose a port to listen on

receive_file(save_received_file, sender_port)