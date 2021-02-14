import socket 
from termcolor import colored


# format that is using for decoding and encoding messages, and header size that is used to determine the length of messages
FORMAT = "utf-8"
HEADERSIZE = 16

# make a header for every message that is going to be send.
# this header contain message length so this way by reading header first 
# server can easily find the length of message
def send_to_server(client_socket, msg):
    msg_length = len(msg)
    header = str(msg_length)
    msg_header = header + " " * (HEADERSIZE - len(header))
    message = (msg_header + msg).encode(FORMAT)
    client_socket.send(message)


# reciev what server sends, first read the header that contain the message length and then read the message itself
def recv_from_server(client_socket):
    msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
    if msg_header:    
        msg_length = int(msg_header.strip(' '))
        data = client_socket.recv(msg_length).decode(FORMAT)
        if data:
            print(data)


def main():

    # target host and port to connect to 
    thost_ipv4 = "127.0.1.1"
    tport = 4444

    # create socket using INET family and tcp type protocol
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # try to connet to target
        client_socket.connect((thost_ipv4, tport))
    except :
        print(colored("[!] failed to connet to target host ip", "red"))
        client_socket.close()
        exit()

    name = input(colored("[*] Enter Your Name: ", "cyan"))
    send_to_server(client_socket, name)
    
    # get data from client and send it to server, repeat this untill client quit by entering q keyword
    while True:
        recv_from_server(client_socket)
        
        data_to_send = input(colored(f"[*] {name}@server #> ", "cyan"))
        send_to_server(client_socket, data_to_send)
        if data_to_send.lower() == 'q' :
            break



if __name__ == "__main__":
    main()