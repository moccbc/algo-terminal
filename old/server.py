import json
import sys
import traceback
import socket
import selectors
import types

sel = selectors.DefaultSelector()
state = {
    'players': 0
}
chatRoom = set() 

def accept_wrapper(sock):
    global state, chatRoom
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)

    chatRoom.add(conn)
    print(chatRoom)
    
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    sel.register(conn, events, data=data)

    state['players'] += 1

    print("Current number of players:", state['players'])

def service_connection(key, mask):
    global state 
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
            sel.modify(sock, selectors.EVENT_WRITE, data=data)
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
            state['players'] -= 1
            print("Current number of players:", state['players'])
    if mask & selectors.EVENT_WRITE:
        if not data.outb:
            info = bytes(json.dumps(state), 'utf-8')
            sock.send(info)
        elif data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            message = 0
            for to in chatRoom:
                if to != sock:
                    print(to)
                    message = sock.send(data.outb)
            data.outb = data.outb[message:]
        sel.modify(sock, selectors.EVENT_READ, data=data)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None: # This is when a client connects.
                accept_wrapper(key.fileobj)
            else:
                try:
                    service_connection(key, mask)
                except Exception:
                    print(f"{traceback.format_exc()}")
                    sel.unregister(key.fileobj)
                    key.fileobj.close()
                    state['players'] -= 1

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

