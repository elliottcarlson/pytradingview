import json
import pprint
import re
import random
import string

import txaio
txaio.use_asyncio()

#from autobahn.asyncio.websocket import WebSocketClientProtocol
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

from pytradingview.eventemitter import EventEmitter

watchlist = {}

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = {}


    def update(self, data):
        self.data.update(data)


#    def isReady(self):
#        if self.data.keys() >= {'lp', 'ch', 'chv'


    def __str__(self):
        print(self.symbol)
        print(f'    sess : {self.data["current_session"]}')
        print(f'    lp   : {self.data["lp"]}')
        print(f'    rtc  : {self.data["rtc"]}')
        print(f'    ch   : {self.data["ch"]}')
        print(f'    rch  : {self.data["rch"]}')
        print(f'    chp  : {self.data["chp"]}')
        print(f'    rchp : {self.data["rchp"]}')
        print('----------------------------------------------')
        return self.symbol + ': ' + str(self.data['lp'] if 'lp' in self.data else 'Loading...')


class Client(WebSocketClientFactory, EventEmitter):
    def __init__(self, loop):
        tv_url = 'wss://data.tradingview.com/socket.io/websocket'
        origin = 'https://data.tradingview.com/'

        super(Client, self).__init__(
            tv_url,
            origin=origin
        )

        self._loop = loop
        #handler = ClientHandler(self.emit)
        #self.protocol = lambda: handler
        self.protocol = lambda: ClientHandler(self.emit)


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

        symbols = [
            'AAPL', 'ACST', 'AGC', 'AHT', 'AIKI', 'AMC', 'AMD', 'AMRS', 'AMZN',
            'BOTY', 'BP', 'BRK.B',
            'CBAT', 'CBT', 'CRSR', 'CRVS', 'CYTH',
            'EXPR',
            'FB',
            'GME',
            'HACK',
            'JNJ',
            'KXIN',
            'LIT', 'LYFT',
            'MOM',
            'NAKD', 'NOK',
            'OKTA', 'OUST',
            'PLAY', 'PLTR',
            'QCLN',
            'RBLX',
            'SAVA', 'SFT', 'SHAK', 'SHOP', 'SNDL', 'SNOW', 'SUBZ', 'SQ',
            'TMBR', 'TSLA', 'TTM',
            'VIG',
            'YOLO',
            'WISH', 'WMT',
            'ZOM'
        ]
        symbols = ['GME']
        for symbol in symbols:
            self.send('quote_add_symbols', [self.quote_session, symbol, {'flags': ['force_permission']}])
#        self.send('quote_add_symbols', [self.quote_session, 'BTCUSD', {'flags': ['force_permission']}])
#        self.send('quote_add_symbols', [self.quote_session, 'AHT', {'flags': ['force_permission']}])
#        self.send('quote_add_symbols', [self.quote_session, 'AMC', {'flags': ['force_permission']}])
#        self.send('quote_add_symbols', [self.quote_session, 'BP', {'flags': ['force_permission']}])
#        self.send('quote_add_symbols', [self.quote_session, 'CRSR', {'flags': ['force_permission']}])


    def onMessage(self, payload, isBinary):
        lines = re.split(r'~m~[0-9]+~m~', payload.decode('utf8'))

        for i in range(len(lines)):
            if lines[i]:
                # Respond to heartbeat
                if re.match(r'^~h~[0-9]+$', lines[i]):
                    self.sendRaw(lines[i])
                    continue

                try:
                    data = json.loads(lines[i])

                    if 'm' in data and data['m'] == 'qsd':
                        if data['p'][0] == self.quote_session and data['p'][1]['s'] == 'ok':
                            symbol = data['p'][1]['n']
                            newdata = data['p'][1]['v']

                            if symbol not in watchlist:
                                watchlist[symbol] = Stock(symbol)

                            watchlist[symbol].update(newdata)

                            self.emit('update', watchlist[symbol])
                except Exception as e:
                    print(f'!!! {e}')
                    print(lines[i])
                    continue


if __name__ == '__main__':
    import asyncio
    import pprint

    loop = asyncio.get_event_loop()

    conn = Client(loop)
    conn.on('connected', lambda: print('Connected!'))
    conn.on('update', lambda x: print(x))
    conn.run()
    print('Starting...')
    loop.run_forever()
    loop.close()
