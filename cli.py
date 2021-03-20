#!/usr/bin/env python3
import asyncio
from cli import ui, Client

loop = asyncio.get_event_loop()

async def run() -> Client:
    client = Client(loop)
    app = ui.Interface(client)
    await client.start()
    return app


if __name__ == '__main__':
    app = loop.run_until_complete(run())
    ui.launch(app, loop)
