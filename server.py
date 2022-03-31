import socket
import select
import time
import RSA

def broadcast_msg(sock, msg):
    now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
    msg = '(' + now_time  + ')\n' + msg
    for socket in CONNECTION_LIST:
        if socket != server_sock and socket != sock:
            try:
                socket.send(msg.encode())
            except:
                socket.close()
                CONNECTION_LIST.remove(socket)


def private_msg(socket, msg):
    now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
    msg = '(' + now_time  + ')\n' + msg
    try:
        socket.send(msg.encode())
    except:
        socket.close()
        CONNECTION_LIST.remove(socket)


def welcome(server_sock):
    sockfd, addr = server_sock.accept()
    CONNECTION_LIST.append(sockfd)
    print(f"New connection from {addr[0]}:{addr[1]}")
    cli_pub_pem = sockfd.recv(1024)
    # print(cli_pub_pem)
    CLIENT_PUBKEY_DICT[addr[1]] = cli_pub_pem
    sockfd.send(public_pem)
    time.sleep(0.1)
    welcome_msg = f"<Server> Welcome {addr[1]} to the chatroom!\n"
    welcome_msg += "<Server> Here are some commands:\n"
    welcome_msg += "<Server> Enter \"/USERS\" to see online users.\n"
    welcome_msg += "<Server> Enter \"/PM <user> <message>\" to send private messages.\n"
    welcome_msg += "<Server> Enter \"/EXIT\" to exit.\n"
    private_msg(sockfd, welcome_msg)
    broadcast_msg(sockfd, f"<Server> User {addr[0]}:{addr[1]} enter the room!\n")


def close(sock):
    addr = sock.getpeername()
    broadcast_msg(sock, f"<Server> User {addr[0]}:{addr[1]} quit the room.\n")
    print(f"{addr[0]}:{addr[1]} offline")
    sock.close()
    CONNECTION_LIST.remove(sock)


def printUsers(sock):
    msg = "<Server> Online users:\n"
    for sok in CONNECTION_LIST[1:]:
        addr = sok.getpeername()
        msg += f"\t{addr[0]}:{addr[1]}\n"
    private_msg(sock, msg)


if __name__ == "__main__":
    CONNECTION_LIST = []
    RECV_BUFFER = 1024
    PORT = 10000
    CLIENT_PUBKEY_DICT = {}

    private_pem, public_pem, random_generator = RSA.RSAInit()

    server_sock = socket.socket()
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", PORT))
    server_sock.listen(100)

    CONNECTION_LIST.append(server_sock)
    print(f"Chatroom server started on port {PORT}")

    while 1:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
        
        for sock in read_sockets:

            if sock == server_sock:
                welcome(sock)

            else:
                data = sock.recv(RECV_BUFFER)
                if not data:
                    close(sock)
                    continue
                
                data_list = data.decode().split()
                if len(data_list)==0 or data_list[0]=='\n':
                    private_msg(sock, "<Server> Please don't send blank message!\n")
                    continue

                cmd = data_list[0]
                if cmd=="/EXIT":
                    close(sock)

                elif cmd=="/USERS":
                    printUsers(sock)

                elif cmd=="/PM":
                    # print(data)
                    addr = sock.getpeername()
                    msg = data_list[1].encode()
                    sig = data_list[3].encode()

                    client_pub_pem = CLIENT_PUBKEY_DICT[addr[1]]
                    if not RSA.RSACheck(msg, sig, client_pub_pem):
                        print(f"Fake Signature from {addr[1]}!")
                        private_msg(sock, "<Server> Fake Signature!\n")
                        continue

                    data = RSA.RSADecode(msg, private_pem, random_generator)
                    data_list = data.decode().split()

                    if len(data_list)<=2:
                        private_msg(sock, "<Server> Usage \"/PM <user> <message>\"\n")
                        continue
                    if not data_list[1].isdigit():
                        private_msg(sock, "<Server> User must be a integer!\n")
                        continue

                    user = int(data_list[1])
                    msg = ' '.join(data_list[2:])
                    msg = f"<PM {addr[1]}> {msg}\n"

                    client_pub_pem = CLIENT_PUBKEY_DICT[user]
                    msg = RSA.RSAEncode(msg.encode(), client_pub_pem)
                    sig = RSA.RSASign(msg, private_pem)
                    msg = (b'/PM ' + msg + b' SIGN ' + sig).decode()

                    for sok in CONNECTION_LIST[1:]:
                        if sok.getpeername()[1]==user:
                            private_msg(sok, msg)
                            break
                        if sok==CONNECTION_LIST[-1]:
                            private_msg(sock, "<Server> User not fonud!\n")

                else:
                    addr = sock.getpeername()
                    broadcast_msg(sock, f"<{addr[0]}:{addr[1]}> {data.decode()}")

    server_sock.close()
