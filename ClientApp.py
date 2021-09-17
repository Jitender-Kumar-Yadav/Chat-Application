import socket
import threading

recv_sock = socket.socket()
send_sock = socket.socket()
active = True

def sendMessage():
    '''
    Allows the thread to send message continuosly
    '''
    global active
    global recv_sock
    global send_sock
    while active:
        read = input().split(" ")
        if read[0] == "CLOSE":
            active = False
        elif read[0][0] != "@":
            print("Please tag a user using @.")
        elif len(read) < 2:
            print("Please do not send empty messages.")
        else:
            send_user = read[0][1:]
            content = " ".join(read[1:])
            send_msg = "SEND " + send_user + " \nContent-length: " + str(len(content)) + " \n\n" + content
            send_sock.send(bytes(send_msg, 'utf-8'))
            reply = str(send_sock.recv(1024), 'utf-8')
            print(reply)
    send_sock.close()

def recvMessage():
    '''
    Allows the thread to recieve message continuosly
    '''
    global active
    global recv_sock
    global send_sock
    while active:
        get = str(recv_sock.recv(4096), 'utf-8').split("\n")
        if len(get) < 4 or len(get[0]) < 2 or len(get[1]) < 2:
            recv_sock.send(bytes("ERROR 103 Header Incomplete\n\n", 'utf-8'))
        else:
            sender = get[0].split(" ")[1]
            length = int(get[1].split(" ")[1])
            msg = get[3][0:length]
            print("\nMessage From " + sender + ":\n" + msg)
    recv_sock.close()



print("Welcome to Jitender's Chat Application. Thank you for choosing us. <3")

# get username and hostname from user
username = input("\nEnter a valid username.\n")
user_check = False
host = input("\nEnter the server's IPv4 address. For local server, use 'local'.\n")
if host == "local":
    host = socket.gethostname()
host_check = False

# establishing contact with server
while not (host_check and user_check):
    try:
        # make connection for sending
        send_sock.connect((host, 10000))
        send_sock.send(bytes("REGISTER TOSEND " + username + "\n\n", 'utf-8'))
        send_response = str(send_sock.recv(1024), 'utf-8')
        print("\n" + send_response.split("\n")[0])
        send_response = (send_response.strip().split("\n")[0]).split(" ")
        
        # make connection for recieving
        recv_sock.connect((host, 10000))
        recv_sock.send(bytes("REGISTER TORECV " + username + "\n\n", 'utf-8'))
        recv_response = str(recv_sock.recv(1024), 'utf-8')
        print(recv_response.split("\n")[0])
        recv_response = (recv_response.strip().split("\n")[0]).split(" ")
        
        if recv_response[0] == "ERROR" and recv_response[1] == "100":
            username = input("User Name already used.\n\nEnter a valid username.\n")
            user_check = False
            send_sock.close()
            recv_sock.close()
            recv_sock = socket.socket()
            send_sock = socket.socket()
        else:
            user_check = True
            host_check = True
        
        # validation message
        if send_response[0] == "REGISTERED" and recv_response[0] == "REGISTERED":
            print("\nNew User " + send_response[2] + " registered at server.\n")
            print("To start a conversation, tag a user. To end application, type CLOSE.\n")
        
    except ConnectionRefusedError:
        host = input("\nServer could not be connected.\nEnter a valid server's IPv4 address. For local server, use 'local'.\n")
        if host == "local":
            host = socket.gethostname()
        send_sock.close()
        recv_sock.close()
        recv_sock = socket.socket()
        send_sock = socket.socket()
        host_check = False

# begin sending and recieving messages
active = True
send_thread = threading.Thread(target = sendMessage, name = "send")
recv_thread = threading.Thread(target = recvMessage, name = "recv")
send_thread.start()
recv_thread.start()
send_thread.join()
recv_thread.join()

print("\nChat Application ended successfully.\nSee you again some other day.\nWarm Regards <3")
