import asyncio
import hashlib

HOST_PORT = 55555
HOST_ADDR = '127.0.0.1'
DELAY = 1 

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(HOST_ADDR, HOST_PORT)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def process(reader, writer):
    data = await reader.readline()
    message = data.decode().strip()
    addr = writer.get_extra_info('peername')
    print(f"Received {message!r} from {addr!r}")
    # Simulate latencies.
    print(f"Wait for {DELAY} seconds")
    reply = hashlib.md5(message.encode()).hexdigest()
    await asyncio.sleep(DELAY)
    print(f"Send: {reply!r}")
    writer.write(reply.encode())
    await writer.drain()
    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(process, HOST_ADDR, HOST_PORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
