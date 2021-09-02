from socket import socket as Sock
import select
from collections import deque
from inspect import getgeneratorstate as genstate
import logging
from typing import Generator


def init_logger() -> logging.Logger:
    logger = logging.getLogger('chat')
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)
    return logger

logger = init_logger()

clients = set()

# Tasks queue 
tasks = deque([])  # generator, that yields the tuple(reason (e.g. write, read), socket)
broadcast_q = {}  # {socket: deque[messages to this client]}

write_queue = {}
read_queue = {}


def run(server_socket: Sock):
    connection_task = accept_connection(server_socket)
    execute_task(connection_task)
    event_loop()


def broadcast():
    for c_sock in broadcast_q.keys():
        while broadcast_q[c_sock]:
            deq: deque = broadcast_q[c_sock]
            msg = deq.popleft()
            task = send_message(c_sock, msg)
            tasks.append(task)


def send_message(client_sock: Sock, msg: bytes):
    cn = client_sock.getsockname()
    cnl = list(cn)
    cnl[-1] = str(cnl[-1])
    cnl = ':'.join(cnl)
    dec = msg.decode('UTF8')
    msg = (cnl+' >> '+dec).encode('UTF8')

    yield 'write', client_sock
    
    logger.info(f'sending message to {client_sock}')
    client_sock.send(msg)


def event_loop():
    while any([tasks, write_queue, read_queue]):
        broadcast()
        while not tasks:
            read_ready, write_ready, _ = select.select(read_queue, write_queue, [])     # blocks while waiting for socket events

            for sock in write_ready:
                generator = write_queue.pop(sock)
                tasks.append(generator)

            for sock in read_ready:
                generator = read_queue.pop(sock)
                tasks.append(generator)

        execute_task()


def execute_task(task: Generator = None):
    if not task:
        task = tasks.popleft()

    try:
        reason, socket = next(task)
        
        if reason == 'read':
            read_queue[socket] = task
        elif reason == 'write':
            write_queue[socket] = task
        else:
            raise Exception('wrong reason')

    except StopIteration:
        print('no more tasks')


def accept_connection(server_sock: Sock):
    while True:

        yield 'read', server_sock
        c_soc, addr = server_sock.accept()  # (read) blocks while waiting for new connection

        logger.info(f'{addr} connected')

        broadcast_q[c_soc] = deque([])

        task = recieve_message(c_soc)
        execute_task(task)


def recieve_message(client_sock: Sock):
        while True:
            yield 'read', client_sock
            msg = client_sock.recv(4096)   # (read) blocks while waiting for new client message

            addr = client_sock.getsockname()
            logger.info(f'Recieving message from {addr}')

            if not msg:
                client_sock.close()
                break
            
            for client in broadcast_q.keys():
                if client != client_sock:
                    broadcast_q[client].append(msg)





'''
Action handlers:
    - New server connection handler
    - New message from the client handler
    - The need to send a message to somebody handler


Workflow:
    - Each action handler is a generator function.
    - Each task is an action handler generator.
    - After the next() call on the new task we get:
        1. The result of handled action
            (message sent, connection established);
        2. Tuple with reason (read or write form socket) and socket,
            which server need to listen for this reason;
    - Write and read dicts contain {socket: action handler generator} pair.

This tuple elemetns is sorted into one of two dicts - read or write queue.
Every dict element looks like {socket to be listened: generator}
'''
