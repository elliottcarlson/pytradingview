import json
import random
import re
import string

from autobahn.asyncio.websocket import WebSocketClientProtocol

from pytradingview.watchlist import WatchList

class Handler(WebSocketClientProtocol):
    def __init__(self, emit):
        super(Handler, self).__init__()

        self.emit = emit
        self.quote_session = self.generateSession('qs')
        self.watchlist = WatchList()


    def generateSession(self, prefix):
        sessionLength = 12
        chars = string.ascii_letters + string.digits
        session = ''.join(random.choice(chars) for i in range(sessionLength))
        return f'{prefix}_{session}'


    def send(self, method, params):
        self.sendSigned(json.dumps({
            'm': method,
            'p': params,
        }, separators=(',', ':')))


    def sendSigned(self, message):
        message = f'~m~{str(len(message))}~m~{message}'.encode('utf8')
        self.sendMessage(message)


    def onOpen(self):
        self.send('set_data_quality', ['low'])
        self.send('set_auth_token', ['unauthorized_user_token'])
        self.send('quote_create_session', [self.quote_session])
        self.send('quote_set_fields', [self.quote_session, "base-currency-logoid", "ch", "chp", "currency-logoid",
            "currency_code", "current_session", "description", "exchange", "format", "fractional", "is_tradable",
            "language", "local_description", "logoid", "lp", "lp_time", "minmov", "minmove2", "original_name",
            "pricescale", "pro_name", "short_name", "type", "update_mode", "volume", "ask", "bid", "fundamentals",
            "high_price", "is_tradable", "low_price", "open_price", "prev_close_price", "rch", "rchp", "rtc",
            "rtc_time", "status", "basic_eps_net_income", "beta_1_year", "earnings_per_share_basic_ttm", "industry",
            "market_cap_basic", "price_earnings_ttm", "sector", "volume", "dividends_yield", "timezone" ])

        self.emit('connected')


    def onMessage(self, payload, isBinary):
        lines = re.split(r'~m~[0-9]+~m~', payload.decode('utf8'))

        for i in range(len(lines)):
            if lines[i]:
                if re.match(r'^~h~[0-9]+$', lines[i]):
                    self.sendSigned(lines[i])
                    continue

                try:
                    data = json.loads(lines[i])

                    if 'm' in data and data['m'] == 'qsd':
                        if data['p'][0] == self.quote_session and data['p'][1]['s'] == 'ok':
                            symbol = data['p'][1]['n']
                            update = data['p'][1]['v']

                            self.watchlist.update(symbol, update)
                            self.emit('update', self.watchlist.get(symbol))
                except Exception as e:
                    self.emit('error', e)
                    continue
