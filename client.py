from collections import deque
import socket
import selectors
import sys

selector = selectors.DefaultSelector()

SOCK: socket.socket
USER_INPUT = sys.stdin

write_queue = []


def handler_connect_to_server() -> socket.socket:
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('localhost', 5588))
    client_sock.setblocking(0)
    return client_sock


def handler_get_input_message(mask):
    msg = USER_INPUT.readline().rstrip()
    write_queue.append(msg.encode('UTF8'))
    

def handler_server_events(mask):
    if mask == selectors.EVENT_READ:
        msg_from_server = SOCK.recv(4096)
        if msg_from_server:
            decoded_msg = msg_from_server.decode('UTF8')
            print(decoded_msg)
        else:
            SOCK.close()

    if mask == selectors.EVENT_WRITE:
        while write_queue:
            SOCK.send(write_queue.pop(0))

            
def event_loop():
    while True:
        events = selector.select()
    
        for selector_key, event_mask in events:
            action_handler = selector_key.data
            action_handler(event_mask)
            

if __name__ == '__main__':
    SOCK = handler_connect_to_server()

    selector.register(
        fileobj=SOCK,
        events=selectors.EVENT_READ | selectors.EVENT_WRITE,
        data=handler_server_events,
    )

    selector.register(
        fileobj=USER_INPUT,
        events=selectors.EVENT_READ,
        data=handler_get_input_message,
    )

    event_loop()


# cn = client_sock.getsockname()
# cnl = list(cn)
# cnl[-1] = str(cnl[-1])
# cnl = ':'.join(cnl)

