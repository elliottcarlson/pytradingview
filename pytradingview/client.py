import json
import logging
from typing import Dict, List

from pytradingview.connection import TradingViewConnection
from pytradingview.event_emitter import EventEmitter, emit

logger = logging.getLogger(__name__)

class TradingViewClient(EventEmitter):
    def __init__(self):
        self._conn = TradingViewConnection()
        #self._conn.set_ws_message_handler(
        #    handler=self._handle_messages
        #)

        self._conn.on('message', self._handle_messages)
        self._conn.connect()


    def _handle_messages(self, message: str):
        msg: Dict = message # json.loads(message)

        self.emit('test', message)
        print(message)

        #logger.info(msg)
