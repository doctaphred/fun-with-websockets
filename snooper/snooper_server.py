#!/usr/bin/env python3

from datetime import datetime
from itertools import count
from pprint import pprint
import asyncio
import json

import websockets


socket_numbers = count()


async def snoop(websocket, path):
    """Pretty-print JSON objects as they are received."""
    socket_number = next(socket_numbers)
    print('Socket {socket_number} ({path}) opened'.format_map(locals()))

    while True:

        if not websocket.open:
            # TODO: does this ever actually happen?
            print('Socket {socket_number} ({path}) exiting'.format_map(locals()))
            break

        received = await websocket.recv()

        if received is None:
            print('Socket {socket_number} ({path}) closed'.format_map(locals()))
            break

        try:
            received = json.loads(received)
        except Exception:
            pass

        print()
        print('Socket {socket_number} ({path}):'.format_map(locals()))
        pprint(received)

        now = datetime.now()
        await websocket.send('{now}: Received message on socket {socket_number} ({path})'.format_map(locals()))


if __name__ == '__main__':
    start_server = websockets.serve(snoop, 'localhost', 1111)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        # TODO: gracefully disconnect clients
        print('Server will shut down when all clients have disconnected...')
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.gather(*pending))
        print('All clients have disconnected.')
    print('Shutting down...')
    loop.close()
