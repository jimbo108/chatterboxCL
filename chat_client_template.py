import socket
import sys
import _thread

def listen_conversation(conn):
    # TODO: check for closed connection
    msg = conn.recv(1024)
    msg = msg.decode()
    print(msg)

PORT = "3490"
DEFAULT_PORT = 3490
BACKLOG = 11
PORT_NUM_PRIME = 64499
HOST = None
UTF_8 = 'utf-8'
uid = 0
argc = len(sys.argv)

argv = str(sys.argv)

print("argc is ", argc)
if argc > 2:
    try:
        checkValidPort = int(argv[2])
        if checkValidPort < 1 or checkValidPort > 65535:
            print("Port outside of range")
            exit()
        port = checkValidPort
    except:
        print("Invalid port argument")
        exit()
else:
    port = DEFAULT_PORT

for result in socket.getaddrinfo(HOST, port, socket.AF_UNSPEC,
                                 socket.SOCK_STREAM):
    af, socktype, proto, cannonname, sa = result
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print("client: failed to connect")
    sys.exit(1)

    uid = s.recv(1024)
    uid = uid.decode()
    print("uid is ", uid)
while 1:
    _thread.start_new_thread(listen_conversation, (s,))
    clientInput = input(str(uid) + ':') # need to cut out num:
                                        # also prints seem to be
                                        # waiting until a send
    s.send(clientInput.encode())

    # socket.recv(1024)  # Leaving this out, "heartbeat" concept not really
    # necessary with timeouts