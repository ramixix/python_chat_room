import socket 
import getpass
from threading import Thread
from termcolor import colored
from time import sleep


# format that is using for decoding and encoding messages, and header size that is used to determine the length of messages
FORMAT = "utf-8"
HEADERSIZE = 16
UserName = ""
UserPass = ""
stop_running = False


""" make a header for every message that is going to be send.this header contain message
length so this way by reading header first server can easily find the length of message"""
def send_to_server(client_socket, msg):
    msg_length = len(msg)
    header = str(msg_length)
    msg_header = header + " " * (HEADERSIZE - len(header))
    message = (msg_header + msg).encode(FORMAT)
    client_socket.send(message)


def get_data(client_socket):
    msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
    if msg_header:
        msg_length =  int(msg_header.strip(" "))
        if msg_length != 0:
            data = client_socket.recv(msg_length).decode(FORMAT)
            return data

# reciev what server sends, first read the header that contain the message length and then read the message itself
def recv_from_server(client_socket):
    global stop_running
    try:
        while True:
            if stop_running == True:
                break
            data = get_data(client_socket)
            if data != "":
                if data == "Username":
                    send_to_server(client_socket, UserName)
                    continue

                elif data == "Again":
                    stop_running = True
                    continue

                elif data == "Password":
                    send_to_server(client_socket, UserPass)
                    continue

                elif data == "WrongPass":
                    print(colored("The password you have entered is invalid", 'red'))
                    stop_running = True
                    continue

                elif data == "KICK":
                    stop_running = True
                    continue

                if  data[:len(UserName)] != UserName:
                    print(colored(data, 'green'))
                else:
                    print("[ME]: " + data[len(UserName) + 1:])
            
    except Exception as e:
        print(colored("[Exception]: " + str(e)  ,'red'))
        exit()


def main():
    global UserName
    global UserPass

    while True:
        UserName = input(colored("[*] Enter Your Name OR a Nickname: ", "cyan"))
        if UserName != "":
            if UserName == "Admin":
                UserPass = getpass.getpass(colored("[*] Enter Password: ", "cyan"))
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
        
    # get data from client and send it to server, repeat this untill client quit by entering q keyword
    #recv_thread = Thread(target=recv_from_server, args=(client_socket, UserName))
    recv_thread = Thread(target=recv_from_server, args=(client_socket,))
    recv_thread.setDaemon(True)
    recv_thread.start()

    while True:
        try:
            if stop_running == True:
                break

            data_to_send = input("")
            if data_to_send != "":
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