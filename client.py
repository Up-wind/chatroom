import sys
import socket
import select

def die(msg):
    print(msg)
    sys.exit()

def prompt():
    sys.stdout.write('\n<Client> ')
    sys.stdout.flush()

if __name__ == "__main__":

    host = '127.0.0.1'
    port = 10000
    sock = socket.socket()
    
    try:
        sock.connect((host,port))
    except:
        die("Connect error")

    while True:
        rlist = [sys.stdin, sock]

        read_list, write_list, error_list = select.select(rlist, [], [])

        for s in read_list:
            if s == sock:
                data = sock.recv(1024)
                if not data:
                    die('Disconnected.')

                else:
                    sys.stdout.write(data.decode())
                    prompt()

            else:
                msg = sys.stdin.readline()
                if msg=="/EXIT\n":
                    sock.send(msg.encode())
                    # sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                    die("<Server> Bye ~")

                else:
                    sock.send(msg.encode())
                    prompt()
