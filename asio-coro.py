import selectors
import socket
import time

# To simpified the project, it doesn't consider Timeout or expecetions.
HOST = '127.0.0.1'
PORT = 55555
RECV_SIZE = 256
NUM = 100

def readUser(id: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Unfortunately, socket.connect function doesn't work with non-blocking I/O directly
    # Since this is only a demo to explain how asynchronous I/O works, I will skip it.
    sock.connect((HOST, PORT)) 
    sock.setblocking(False)

    sock.sendall(f"{id}\n".encode()) 
    yield (sock, selectors.EVENT_WRITE)

    yield (sock, selectors.EVENT_READ)
    data = sock.recv(RECV_SIZE)  # Should be ready
    message = data.decode()
    
    print(f"{id}: {message}")
    yield (None, message)

def start_loop(generators):
    selector = selectors.DefaultSelector()
    queue = generators

    # when there is any coroutine wait for calculate:
    while queue:
        # execute all the generators in the queue
        for coro in queue:
            sock, rw_flag =  next(coro)
            if sock:
                selector.register(sock, rw_flag, coro)        
        queue.clear() # empty queue

        # No more coroutine waiting to run, we need to wait for I/O
        events = selector.select()
        for key, _ in events:
            selector.unregister(key.fileobj)
            queue.append(key.data)


start = time.time()
start_loop([readUser(0)])
period = time.time() - start
print(f"Reading 1 user data takes {period} seconds")

start = time.time()
start_loop([readUser(id) for id in range(NUM)])
period = time.time() - start
print(f"Reading {NUM} users data takes {period} seconds")
