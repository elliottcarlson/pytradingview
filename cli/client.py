import asyncio
from contextlib import suppress

from cli.event_emitter import EventEmitter, emit
from cli.utils import reify


class Client(EventEmitter):
    def __init__(self, loop):
        self.time = 0.25
        self.is_started = False
        self.index = 1
        self._task = None
        self.loop = loop


    async def start(self):
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.ensure_future(self._run())


    async def stop(self):
        if self.is_started:
            self.is_started = False
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task


    async def _run(self):
        while True:
            await asyncio.sleep(self.time)
            self.emit('test', self.index)
            self.index += 1
