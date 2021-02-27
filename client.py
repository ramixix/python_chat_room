import socket 
import getpass
from threading import Thread
from termcolor import colored
from time import sleep


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
def recv_from_server(client_socket, name):
    try:
        while True:
            msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
            if msg_header:
                msg_length =  int(msg_header.strip(" "))
                if msg_length != 0:
                    data = client_socket.recv(msg_length).decode(FORMAT)
                    if data != "":
                        if data == "Wrong Password":
                            break
                        if  data[:len(name)] != name:
                            print(colored(data, 'green'))
                        else:
                            print("[ME]: " + data[len(name) + 1:])
            
    except Exception as e:
        print(colored("[Exception]: " + str(e)  ,'red'))
        exit()


def main():
    while True:
        name = input(colored("[*] Enter Your Name OR a Nickname: ", "cyan"))
        if name != "":
            if name == "Admin":
                passwd = getpass.getpass(colored("[*] Enter Password: ", "cyan"))
            break

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
        
    send_to_server(client_socket, name)
    # if specified name is equal to Admin then ask for password and send password to server
    if name == "Admin":
        send_to_server(client_socket, passwd)
        # after sending password to server wait to receive response from the server and if the reponse be equal to-'
        #  'Wrong Password!!!' then exit otherwise print the response.
        msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
        if msg_header:
            msg_length =  int(msg_header.strip(" "))
            if msg_length != 0:
                data = client_socket.recv(msg_length).decode(FORMAT)
                if data != "":
                    if data == "Wrong Password!!!":
                        print(colored(data, 'red'))
                        exit(0)
                    else:
                        print(colored(data, 'cyan'))

    
    # get data from client and send it to server, repeat this untill client quit by entering q keyword
    recv_thread = Thread(target=recv_from_server, args=(client_socket, name))
    recv_thread.setDaemon(True)
    recv_thread.start()

    while True:
        try:
            data_to_send = input("")
            send_to_server(client_socket, data_to_send)
            if data_to_send.lower() == 'q' :
                break
        except KeyboardInterrupt:
            # after keyboard interrupt[CTRL-C] send 'q' to server to make sure that server will remove the clinet from the clinets list
            print(colored("Existing...", 'red'))
            send_to_server(client_socket, 'q')
            break
       
    client_socket.close()



if __name__ == "__main__":
    main()