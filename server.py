import socket
import loop

# selector = loop.selector

def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('localhost', 5588))
    server_sock.setblocking(0)
    server_sock.listen(100)
    return server_sock

if __name__ == '__main__':
    server_sock = start_server()
    loop.run(server_sock)
