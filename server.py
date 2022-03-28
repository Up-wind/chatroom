import socket
import select
import time

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

def close(sock):
    addr = sock.getpeername()
    broadcast_msg(sock, f"<Server> User {addr[0]}:{addr[1]} quit the room.\n")
    print(f"{addr[0]}:{addr[1]} offline")
    sock.close()
    CONNECTION_LIST.remove(sock)


if __name__ == "__main__":
    CONNECTION_LIST = []
    RECV_BUFFER = 1024
    PORT = 10000

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
                sockfd, addr = server_sock.accept()
                CONNECTION_LIST.append(sockfd)
                print(f"New connection from {addr[0]}:{addr[1]}")
                sockfd.send("<Server> Welcome to the chatroom!\n".encode() +
                            "<Server> Here are some codes:\n".encode() +
                            "<Server> Enter \"/USERS\" to see online users.\n".encode() +
                            "<Server> Enter \"/PM <user> <message>\" to send private messages.\n".encode() +
                            "<Server> Enter \"/EXIT\" to exit.\n".encode()
                            )
                broadcast_msg(sockfd, f"<Server> User {addr[0]}:{addr[1]} enter the room!\n")

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
                    msg = "<Server> Online users:\n"
                    for sok in CONNECTION_LIST[1:]:
                        addr = sok.getpeername()
                        msg += f"\t{addr[0]}:{addr[1]}\n"
                    private_msg(sock, msg)

                elif cmd=="/PM":
                    if len(data_list)<=2:
                        private_msg(sock, "<Server> Usage \"/PM <user> <message>\"\n")
                        continue
                    if not data_list[1].isdigit():
                        private_msg(sock, "<Server> User must be a integer!\n")
                        continue
                    user = int(data_list[1])
                    msg = ' '.join(data_list[2:])
                    msg = f"<PM {user}> {msg}\n"
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
