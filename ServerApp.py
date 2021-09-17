import socket
import threading

send_users = {}
recv_users = {}
threads = []

# create the server socket
server = socket.socket()
host = socket.gethostname()
server.bind((host, 10000))
server.listen()

def sendReqAccept(reg_req, conn_socket, addr):
    # analyse registration request for TOSEND and send response
    global send_users
    global recv_users
    global thread
    user = reg_req[2]
    if len(reg_req) == 3 and user[0].isalpha() and user.isalnum() and user not in send_users.keys() and not user == "ALL":
        conn_socket.send(bytes("REGISTERED TOSEND " + user + "\n\n", 'utf-8'))
        send_users[user] = conn_socket
        print("New user '" + user + "' connected to send messages at", addr)
    else:
        conn_socket.send(bytes("ERROR 100 Malformed username\n\n", 'utf-8'))

    # send message to requested clients
    while True:
        try:
            request = str(conn_socket.recv(4096), 'utf-8').split("\n")
            if len(request) < 4 or len(request[0].split(" ")) < 2 or len(request[1].split(" ")) < 2:
                conn_socket.send(bytes("ERROR 103 Header incomplete\n\n", 'utf-8'))
            else:
                send_to = request[0].split(" ")[1]
                msg = request[3][0:int(request[1].split(" ")[1])]
                if not send_to == "ALL" and send_to not in recv_users.keys():
                    conn_socket.send(bytes("ERROR 102 Unable to send\n\n", 'utf-8'))
                else:
                    try:
                        if send_to == "ALL":
                            for reciever in recv_users.keys():
                                if not reciever == user:
                                    recv_users[reciever].send(bytes("FORWARD " + user + "\nContent-length: " + str(len(msg)) + "\n\n" + msg, 'utf-8'))
                        else:
                            recv_users[send_to].send(bytes("FORWARD " + user + "\nContent-length: " + str(len(msg)) + "\n\n" + msg, 'utf-8'))
                        conn_socket.send(bytes("SENT " + send_to + "\n\n", 'utf-8'))
                    except:
                        conn_socket.send(bytes("ERROR 102 Unable to send\n\n", 'utf-8'))
        except BrokenPipeError:
            send_users[user].close()
            recv_users[user].close()
            print("User '" + user + "' at", addr, "has left the server.\n")
            del send_users[user]
            del recv_users[user]
            break

def recvReqAccept(reg_req, conn_socket, addr):
    # analyse registration request for TORECV and send response
    global send_users
    global recv_users
    global thread
    user = reg_req[2]
    if len(reg_req) == 3 and user[0].isalpha() and user.isalnum() and user not in recv_users.keys() and not user == "ALL":
        conn_socket.send(bytes("REGISTERED TORECV " + user + "\n\n", 'utf-8'))
        recv_users[user] = conn_socket
        print("New user '" + user + "' connected to receive messages at", addr, "\n")
    else:
        conn_socket.send(bytes("ERROR 100 Malformed username\n\n", 'utf-8'))

while True:
    # accept connection request
    req, addr = server.accept()
    reg_req = (str(req.recv(1024), 'utf-8').split("\n")[0]).split(" ")
    print('Got ' + reg_req[1] + ' connection request from', addr)
    if reg_req[0] != "REGISTER":
        req.send(byte("ERROR 101 No User Registered\n\n", 'utf-8'))
    elif reg_req[1] == 'TOSEND':
        thr = threading.Thread(target = sendReqAccept, args = (reg_req, req, addr))
        threads.append(thr)
        thr.start()
    else:
        thr = threading.Thread(target = recvReqAccept, args = (reg_req, req, addr))
        threads.append(thr)
        thr.start()

        









