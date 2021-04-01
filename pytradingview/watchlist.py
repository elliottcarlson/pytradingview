from pytradingview.stock import Stock

class WatchList:
    def __init__(self):
        self.watchlist = {}


    def update(self, symbol, data):
        if symbol not in self.watchlist:
            self.watchlist[symbol] = Stock(symbol)

        self.watchlist[symbol].update(data)


    def get(self, symbol):
        if symbol in self.watchlist:
            return self.watchlist[symbol]

