#!/usr/bin/env python3
import asyncio
import json
import nest_asyncio
nest_asyncio.apply()

from cli import Interface, Parser, launch
from pytradingview import TradingViewClient

loop = asyncio.get_event_loop()
parser = Parser()

def loadWatchlist(client):
    symbols = ['AAPL', 'AMC', 'GME', 'WMT']
    symbols = ["GILD", "UNP", "UTX", "HPQ", "V", "CSCO", "SLB", "AMGN", "BA", "COP", "CMCSA", "BMY", "VZ", "T", "UNH",
    "MCD", "PFE", "ABT", "FB", "DIS", "MMM", "ORCL", "PEP", "HD", "JPM", "INTC", "WFC", "MRK", "KO", "AMZN", "PG",
    "BRK.B", "GOOGL", "WMT", "CVX", "JNJ", "MO", "IBM", "GE", "MSFT", "AAPL", "XOM"]
    for symbol in symbols:
        client.watch(symbol)


def parseIncoming(event):
    parsed = parser.parse(event.get('text'))
    if parsed is not None:
        method = parsed[0]


async def run() -> Interface:
    app = Interface()
    tradingview = TradingViewClient(loop)

    app.on('message', lambda x: app.send_message(str(tradingview.quote(x['text']))))

    tradingview.on('connected', lambda: loadWatchlist(tradingview))
    tradingview.on('update', lambda x: app.send_message(str(x)))
    tradingview.on('error', lambda x: app.send_message(f'Error: {x}'))
    tradingview.start()

    return app


if __name__ == '__main__':
    app = loop.run_until_complete(run())
    launch(app, loop)

