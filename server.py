import socket
from termcolor import colored
import threading
import hashlib
from time import sleep

FORMAT = "utf-8"
HEADERSIZE = 16
clients_list = []
Admin_pass = "adfb6dd1ab1238afc37acd8ca24c1279f8d46f61907dd842faab35b0cc41c6e8ad84cbdbef4964b8334c22c4985c2387d53bc47e6c3d0940ac962f521a127d9f"

Puase = None
# anytime a client is conneted to server, Client class used to make an object instance for that client
class Client:
    def __init__(self, sock, ip, port):
        self.sock = sock
        self.ip = ip
        self.port = port
        self.name = None
        self.passwd = None

    def setname(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Client({self.ip}, {self.port})"


def leaving_chatroom(client_obj, msg):
    if len(clients_list) != 1:
        client_obj.sock.close()
        clients_list.remove(client_obj)   
        broadcast(msg)
    else:
        client_obj.sock.close()
        clients_list.remove(client_obj)   


def get_data(client_socket):
    msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
    if msg_header:
        msg_length = int(msg_header.strip(" "))
        if msg_length != 0:
            data = client_socket.recv(msg_length).decode(FORMAT)
            return data


def find_active_users():
    active_users_list = []
    active_users_number = 0
    if len(clients_list) > 0 :
        for client in clients_list:
            active_users_list.append(client.name)
            active_users_number += 1 
    return (active_users_list, active_users_number)


def send_to_client(client_socket, msg):
    msg_length = len(msg)
    header = str(msg_length)
    msg_header = header + " " * (HEADERSIZE - len(header))
    message = (msg_header + msg).encode(FORMAT)
    client_socket.send(message)


# broadcast function is used to send a message to all clients inside clients_list
def broadcast(msg):
    for client in clients_list:
        send_to_client(client.sock, msg)


# This function is get called just when connected client name is 'Admin'
# and asks client for Admin password and compare it to 'Admin_pass' password
def asks_password(client_obj):
    client_socket = client_obj.sock
    Is_Admin = False
    send_to_client(client_socket, "Password")
    passwd = get_data(client_socket).encode(FORMAT)
    if hashlib.sha512(passwd).hexdigest() == Admin_pass:
        client_obj.passwd = passwd
        Is_Admin = True
        return Is_Admin
    else: 
        return Is_Admin


""" receive the first data that clients send and that would be name and  if connected client 
be 'Admin' then ask for password,check Admin enter right password and add it to clients_list
otherwise send 'Wrong Password!!!' message to client and don't add it to clinets_list"""
def verify_clinet(client_obj):
    Is_Client_Valid = True
    client_socket = client_obj.sock
    send_to_client(client_socket, "Username")

    name = get_data(client_socket)
    if len(clients_list) > 0:
        for client in clients_list:
            if name == client.name:
                send_to_client(client_socket, "[Error] A user already exists for the user name specified. Please register again using a different user name.")
                send_to_client(client_socket, "Again")
                Is_Client_Valid = False
                return Is_Client_Valid     

    client_obj.setname(name)

    if name == "Admin":
        is_admin = asks_password(client_obj)
        if is_admin == False:
            send_to_client(client_socket, "WrongPass")
            Is_Client_Valid = False
            return Is_Client_Valid

    send_to_client(client_socket, f"Welcom To Chat Room {name} :)")
    current_active_users_number = find_active_users()[1]
    send_to_client(client_socket, f"{current_active_users_number} User(s) Are Currently Active(Enter 's' to display a list of active user)")
    broadcast(f"****** '{name}' Joined Us!!! ******")
    clients_list.append(client_obj)
    return Is_Client_Valid


def admin_functions(data):
    global Puase
    action = data[1:2]
    if action.lower() == 'k':
        users_to_kick = data.split(" ")[1:]
        for user in users_to_kick:
            for client in clients_list:
                if user == client.name:
                    send_to_client(client.sock, "You Have Been Kicked by Admin!!!")
                    client.sock.close()
                    clients_list.remove(client)
                    broadcast(f"[-] clinet \"{client.name}\" has been kicked by admin from the chat.")
                    break
    elif action.lower() == 'p':
        pause_for_sec = data.split(" ")[1]
        Puase = int(pause_for_sec)


""" make a header for every message that is going to be send. this header contain message 
length so this way by reading header first client can easily find the length of message"""
def client_handler(client_obj):
    client_socket = client_obj.sock
    name = client_obj.name
    while True:
        try:     
            data = get_data(client_socket)
            if data != "":
                if data.startswith("!"):
                    if name == "Admin":
                        admin_functions(data)
                    else:
                        send_to_client(client_socket, "Permission denied, are you Admin?")
                    continue

                if data.lower() == "q":
                    leaving_chatroom(client_obj, f"[-] clinet \"{name}\" left the chat")
                    break

                elif data.lower() == "s":
                    current_active_users_list = find_active_users()[0]
                    send_to_client(client_socket, f"Active users: {current_active_users_list}")
                    continue

                else:
                    broadcast_thread = threading.Thread(target=broadcast, args=(name + ": " + data,))
                    broadcast_thread.start()
                    print(colored(f"[+] Data received from {client_obj.ip} port {client_obj.port} : {data}", 'green'))

        except Exception as e :
            print(colored("[EXCEPTION]" + str(e) , 'red')) 
            leaving_chatroom(client_obj, f"-] clinet \"{name}\" left duo to some connection error")
            break
        

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
            print(colored(f"[*] Recieve connection from {address[0]} port {address[1]}", 'yellow'))
            client_obj = Client(connected_client, address[0], address[1])
            if verify_clinet(client_obj) == True:
                client_thread = threading.Thread(target=client_handler, args=(client_obj,))
                client_thread.setDaemon(True)
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