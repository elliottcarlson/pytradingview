import asyncio

from autobahn.asyncio.websocket import WebSocketClientFactory

from pytradingview.eventemitter import EventEmitter
from pytradingview.handler import Handler as ClientHandler


class Client(WebSocketClientFactory, EventEmitter):
    wss = 'wss://data.tradingview.com/socket.io/websocket'
    host = 'data.tradingview.com'
    port = 443
    ssl = True
    origin = 'https://data.tradingview.com/'

    def __init__(self, loop):
        super(Client, self).__init__(self.wss, origin=self.origin)

        self._loop = loop
        self.handler = ClientHandler(self.emit)
        self.protocol = lambda: self.handler


    def start(self):
        coro = self._loop.create_connection(self, self.host, self.port, ssl=self.ssl)
        self._loop.run_until_complete(coro)
        #asyncio.ensure_future(asyncio.gather(coro))


    def watch(self, symbol):
        self.handler.send('quote_add_symbols', [self.handler.quote_session, symbol, {'flags': ['force_permission']}])
        self.handler.send('quote_fast_symbols', [self.handler.quote_session, symbol])


    def quote(self, symbol):
        return self.handler.watchlist.get(symbol)
