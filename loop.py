import select
from collections import deque
from typing import Generator

tasks = deque([])  # generator, that yields the tuple(reason (e.g. write, read), socket)
clients = set()  # {socket: deque[messages to this client]}

write_queue = {}
read_queue = {}


def start_event_loop():
    while any([tasks, write_queue, read_queue]):
        while not tasks:
            read_ready, write_ready, _ = select.select(read_queue, write_queue, [])     # blocks while waiting for socket events

            for sock in write_ready:
                generator = write_queue.pop(sock)
                tasks.append(generator)

            for sock in read_ready:
                generator = read_queue.pop(sock)
                tasks.append(generator)

        execute_task()


def add_task(task: Generator):
    tasks.append(task)


def execute_task():
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
        print('some task has ended')
