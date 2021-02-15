import socket
from termcolor import colored
import threading

FORMAT = "utf-8"
HEADERSIZE = 16
clients_list = []

class Client:
    def __init__(self, sock, ip, port):
        self.sock = sock
        self.ip = ip
        self.port = port
        self.name = None

    def setname(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Client({self.ip}, {self.port})"



def send_to_client(client_socket, msg):
    msg_length = len(msg)
    header = str(msg_length)
    msg_header = header + " " * (HEADERSIZE - len(header))
    message = (msg_header + msg).encode(FORMAT)
    client_socket.send(message)


def broadcast(msg):
    for client in clients_list:
        send_to_client(client.sock, msg)


def asks_client_name(client_obj):
    client_socket = client_obj.sock
    msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
    if msg_header:
        msg_length =  int(msg_header.strip(" "))
        name = client_socket.recv(msg_length).decode(FORMAT)
        client_obj.setname(name)
        send_to_client(client_socket, f"Welcom To Chat Room {name} :)")
        broadcast(f"****** '{name}' Joined Us!!! ******")


# make a header for every message that is going to be send.
# this header contain message length so this way by reading header first 
# client can easily find the length of message
def client_handler(client_obj):
    client_socket = client_obj.sock
    name = client_obj.name
    try:
        while True:
            msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
            if msg_header:
                msg_length =  int(msg_header.strip(" "))
                if msg_length != 0:
                    data = client_socket.recv(msg_length).decode(FORMAT)
                    if data.lower() == "q":
                        if len(clients_list) != 1:
                            client_socket.close()
                            clients_list.remove(client_obj)   
                            broadcast(f"[-] clinet \"{name}\" left the chat")
                            break
                        else:
                            client_socket.close()
                            clients_list.remove(client_obj)   
                            break

                    if data != "":
                        broadcast_thread = threading.Thread(target=broadcast, args=(name + ": " + data,))
                        broadcast_thread.start()
                        #broadcast(name + ": " + data)
                        print(colored(f"[+] Data received from {client_obj.ip} port {client_obj.port} : {data}", 'green'))
    except Exception as e :
        print(colored("[EXCEPTION]" + str(e) , 'red')) 
        client_socket.close
        clients_list.remove(client_obj)           

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
            connected_client, address = server_socket.accept()
            client_obj = Client(connected_client, address[0], address[1])
            asks_client_name(client_obj)
            clients_list.append(client_obj)
            print(colored(f"[*] Recieve connection from {address[0]} port {address[1]}", 'yellow'))
            client_thread = threading.Thread(target=client_handler, args=(client_obj,))
            client_thread.start()
    
    except KeyboardInterrupt:
        print(colored("\n[!] Closing Server ", 'yellow'))
        server_socket.close()
        for client in clients_list:
            client.close()
            clients_list.remove(client)
        exit(0)


if __name__ == "__main__":
    main()