import sys
import socket
import select
import RSA


def die(msg):
    print(msg)
    sys.exit()

def prompt():
    sys.stdout.write('\n<Client> ')
    sys.stdout.flush()


if __name__ == "__main__":

    private_pem, public_pem, random_generator = RSA.RSAInit()

    host = '127.0.0.1'
    port = 10000

    sock = socket.socket()
    
    try:
        sock.connect((host,port))
    except:
        die("Connect error")

    sock.send(public_pem)

    while True:
        rlist = [sys.stdin, sock]

        read_list, write_list, error_list = select.select(rlist, [], [])

        for s in read_list:

            if s == sock:

                data = sock.recv(1024)
                if not data:
                    die('Disconnected.')

                data_list = data.decode().split()
                if data_list[0] == "-----BEGIN":
                    server_pub_pem = data.decode()
                    # print(server_pub_pem)
                    continue
                
                elif data_list[1] == "/PM":
                    time = data_list[0]
                    msg = data_list[2].encode()
                    sig = data_list[4].encode()

                    if not RSA.RSACheck(msg, sig, server_pub_pem):
                        print("Fake Signature from server!")
                        continue

                    msg = RSA.RSADecode(msg, private_pem, random_generator)
                    sys.stdout.write(time + '\n' + msg.decode())
                    prompt()

                else:
                    sys.stdout.write(data.decode())
                    prompt()

            else:
                msg = sys.stdin.readline()
                msg_list = msg.split()

                # print(len(msg_list))
                if len(msg_list) >= 1:
                    
                    cmd = msg_list[0]
                    if cmd=="/EXIT":
                        sock.send(msg.encode())
                        sock.close()
                        die("<Server> Bye ~")

                    elif cmd=="/PM":
                        msg = RSA.RSAEncode(msg.encode(), server_pub_pem)
                        sig = RSA.RSASign(msg, private_pem)
                        sock.send(b'/PM ' + msg + b' SIGN ' + sig)
                        prompt()

                    else:
                        sock.send(msg.encode())
                        prompt()
                        
                else:
                    sock.send(msg.encode())
                    prompt()
