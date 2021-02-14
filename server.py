import socket
from termcolor import colored
import threading

FORMAT = "utf-8"
HEADERSIZE = 16
clients_list = []
client_msgs = []

class Clinet:
    def __init__(self, sock, ip, port):
        self.name = ""
        self.sock = sock
        self.ip = ip
        self.port = port

    def setname(self, name):
        self.name = name


def send_to_client(client_socket, msg):
    msg_length = len(msg)
    header = str(msg_length)
    msg_header = header + " " * (HEADERSIZE - len(header))
    message = (msg_header + msg).encode(FORMAT)
    client_socket.send(message)

def broadcast(cli, msg):
    for client in clients_list:
        send_to_client(client.sock, cli.name + msg)

# make a header for every message that is going to be send.
# this header contain message length so this way by reading header first 
# client can easily find the length of message

    

def client_handler(client_socket, addr):

    client_obj = Clinet(client_socket, addr[0], addr[1])
    msg_header = client_obj.sock.recv(HEADERSIZE).decode(FORMAT)
    if msg_header:
            msg_length =  int(msg_header.strip(" "))
            client_obj.setname(client_obj.sock.recv(msg_length).decode(FORMAT))
            clients_list.append(client_obj)
    
    broadcast(client_obj, " Joined Us!!!")

    while True:
        msg_header = client_obj.sock.recv(HEADERSIZE).decode(FORMAT)
        if msg_header:
            msg_length =  int(msg_header.strip(" "))
            data = client_obj.sock.recv(msg_length).decode(FORMAT)
            if data.lower() == "q":
                if len(clients_list) != 1:
                    broadcast(client_obj, f"[-] clinet {client_obj.name} left the chat")
                    client_obj.sock.close()
                    clients_list.remove(client_obj)   
                    break
                else:
                    client_obj.sock.close()
                    clients_list.remove(client_obj)   
                    break

            if data != "":
                broadcast(client_obj, ": " + data)
                print(colored(f"[+] Data received from {addr[0]} port {addr[1]} : {data}", 'green'))
          

def main():

    # ipv4 and port to bind to (ip will be the local address of the computer that server is going to run on.)
    bind_ip = socket.gethostbyname(socket.gethostname())
    bind_port = 4444
    BindADDR = (bind_ip, bind_port)

    # create server socket using INET family and tcp type protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # bind to specified ip and port 
        server_socket.bind( BindADDR )
        print(colored(f"[*] Listening on {bind_ip}:{bind_port}", 'cyan'))
    except:
        print(colored("[!] falid to bind", 'red'))
        server_socket.close()
        exit(0)

    # start listening with a maximum backlog of connections set to 5
    try:
        server_socket.listen(5)
        while True:
            # wait for incoming connection and after recieving one, we use threads to handle connections
            connected_client, addr = server_socket.accept()
            print(colored(f"[*] Recieve connection from {addr[0]} port {addr[1]}", 'yellow'))
            client_thread = threading.Thread(target=client_handler, args=(connected_client, addr))
            client_thread.start()
    
    except KeyboardInterrupt:
        print(colored("\n[!] Closing Server ", 'yellow'))
        server_socket.close()
        exit(0)


if __name__ == "__main__":
    main()