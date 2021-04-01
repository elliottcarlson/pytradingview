class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = {}


    def update(self, data):
        self.data.update(data)


    def __str__(self):
        return (
            f'{self.symbol}: '
            f'lp: {self.data["lp"] if "lp" in self.data else "None"}, '
            f'ch: {self.data["ch"] if "ch" in self.data else "None"}, '
            f'chp: {self.data["chp"] if "chp" in self.data else "None"}, '
            f'rtc: {self.data["rtc"] if "rtc" in self.data else "None"}, '
            f'rch: {self.data["rch"] if "rch" in self.data else "None"}, '
            f'rchp: {self.data["rchp"] if "rchp" in self.data else "None"}, '
            f'session: {self.data["current_session"] if "current_session" in self.data else "None"}'
        )
