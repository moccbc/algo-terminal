import json
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

def start_connections(host, port):
    server_addr = (host, port)
    connid = 1
    print(f"Starting connection {connid} to {server_addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    sel.register(sock, selectors.EVENT_READ)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"Received {recv_data!r} from connection")
            state = json.loads(recv_data)
            print(f"Received {state} from connection")
            if 'players' in state:
                if (state['players'] == 2):
                    events = selectors.EVENT_WRITE | selectors.EVENT_READ
                    print("2 players in room")
                    sel.modify(sock, events, data=data)
                else:
                    print("You are the only player")
                    sel.modify(sock, selectors.EVENT_WRITE, data=data)
            elif 'message' in state:
                sel.modify(sock, selectors.EVENT_WRITE, data=data)


    if mask & selectors.EVENT_WRITE:
        print("Input message to send!")
        message = input()
        print(f"Sending {message!r} to connection")
        obj = {'message': message}
        obj_json = bytes(json.dumps(obj), 'utf-8')
        sent = sock.send(obj_json)
        sel.modify(sock, selectors.EVENT_READ, data=data)

host, port = sys.argv[1], int(sys.argv[2])

try:
    start_connections(host, port)
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            service_connection(key, mask)

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
