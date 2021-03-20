import json
import re
import random
import string

from autobahn.asyncio.websocket import WebSocketClientProtocol
from autobahn.asyncio.websocket import WebSocketClientFactory

from pytradingview.event_emitter import EventEmitter

watchlist = {}

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = {}


    def update(self, data):
        self.data.update(data)


class Client(WebSocketClientFactory, EventEmitter):
    def __init__(self, loop):
        tv_url = 'wss://data.tradingview.com/socket.io/websocket'
        origin = 'https://data.tradingview.com/'

        super(Client, self).__init__(
            tv_url,
            origin=origin
        )

        self._loop = loop
        handler = ClientHandler(self.emit)
        self.protocol = lambda: handler


    def run(self):
        coro = self._loop.create_connection(self, 'data.tradingview.com', 443, ssl=True)
        self._loop.run_until_complete(coro)


    def send(self, obj):
        self.protocol.sendJSON(obj)


class ClientHandler(WebSocketClientProtocol):
    def __init__(self, emit):
        super(ClientHandler, self).__init__()
        self.emit = emit
        self.quote_session = self.generateSession('qs_')


    def generateSession(self, prefix):
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(stringLength))
        return prefix + random_string


    def sendRaw(self, message):
        message = f'~m~{str(len(message))}~m~{message}'.encode('utf8')
        print(f'>> {message}')
        self.sendMessage(message)


    def sendJSON(self, obj):
        self.sendRaw(json.dumps(obj))


    def send(self, func, params):
        self.sendRaw(json.dumps({
            'm': func,
            'p': params,
        }, separators=(',', ':')))


    def onOpen(self):
        self.emit('connected')

        self.send('set_data_quality', ['low'])
        self.send('set_auth_token', ['unauthorized_user_token'])
        self.send('quote_create_session', [self.quote_session])

        self.send('quote_add_symbols', [self.quote_session, 'XLMUSD', {'flags': ['force_permission']}])


    def onMessage(self, payload, isBinary):
        lines = re.split(r'~m~[0-9]+~m~', payload.decode('utf8'))
        for i in range(len(lines)):
            if lines[i]:
                try:
                    data = json.loads(lines[1])

                    if 'm' in data:
                        if data['p'][0] == self.quote_session and data['p'][1]['s'] == 'ok':
                            symbol = data['p'][1]['n']
                            newdata = data['p'][1]['v']

                            if symbol not in watchlist:
                                watchlist[symbol] = Stock(symbol)

                            watchlist[symbol].update(newdata)

                            self.emit('update', watchlist[symbol])
                except Exception as e:
                    print(e)
                    if re.match(r'^~h~[0-9]+$', lines[i]):
                        self.sendRaw(lines[i])
                        continue


if __name__ == '__main__':
    import asyncio
    import pprint

    loop = asyncio.get_event_loop()

    conn = Client(loop)
    conn.on('connected', lambda: print('Connected!'))
    conn.on('update', lambda x: pprint.pprint(x.data))
    conn.run()

    loop.run_forever()
    loop.close()
