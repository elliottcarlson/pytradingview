import json
import logging
import re
import time

from threading import Lock, Thread
from websocket import WebSocketApp, WebSocketConnectionClosedException

from pytradingview.event_emitter import EventEmitter

logger = logging.getLogger(__name__)

class TradingViewConnection(EventEmitter):
    def __init__(self,):
        self._ws = None
        self._ws_connect_lock = Lock()
        self._ws_message_handler = lambda x: x


    @property
    def ws(self) -> WebSocketApp:
        return self._ws


    @property
    def ws_uri(self) -> str:
        return 'wss://data.tradingview.com/socket.io/websocket'


    @property
    def ws_origin(self) -> str:
        return 'https://data.tradingview.com'


    @property
    def ws_connect_timeout_seconds(self) -> int:
        return 5


    @property
    def ws_connect_headers(self) -> list:
        return []


    def set_ws_message_handler(self, handler: callable):
        self._ws_message_handler = handler


    def send_json(self, message: dict) -> None:
        self.send_raw(json.dumps(message))


    def send_raw(self, message: str) -> None:
        self.connect()
        self.ws.send(message)


    def connect(self) -> None:
        if self._ws:
            return
        with self._ws_connect_lock:
            while not self._ws:
                self._connect()
                if self._ws:
                    return


    def reconnect(self) -> None:
        if self._ws is not None:
            self._reconnect(self._ws)


    def _connect(self) -> None:
        assert not self._ws, 'websocket should be closed before attempting to connect'

        self._ws = WebSocketApp(
            url=self.ws_uri,
            on_message=self._wrap_callback(self._on_ws_message_callback),
            on_close=self._wrap_callback(self._on_ws_close_callback),
            on_error=self._wrap_callback(self._on_ws_error_callback),
            header=self.ws_connect_headers,
        )

        ws_thread = Thread(target=self._run_websocket, args=(self._ws,))
        ws_thread.daemon = True
        ws_thread.start()

        ts = time.time()
        while self._ws and (not self._ws.sock or not self._ws.sock.connected):
            if time.time() - ts > self.ws_connect_timeout_seconds:
                self._ws = None
                return
            time.sleep(0.1)


    def _run_websocket(self, ws: WebSocketApp) -> None:
        try:
            ws.on_open = self._wrap_callback(self._on_ws_open_callback)
            ws.run_forever(origin=self.ws_origin)
        except Exception as e:
            raise Exception(f'Unexpected error while running websocket: {e}')
        finally:
            self._reconnect(ws)


    def _reconnect(self, ws: WebSocketApp) -> None:
        assert ws is not None, '_reconnect should only be called with an existing ws'
        if ws is self._ws:
            self._ws = None
            ws.close()
            self.connect()


    def _on_ws_message_callback(self, ws: WebSocketApp, message: str):
        logger.info(f'>>> RECV: {message}')
        lines = re.split(r'~m~[0-9]+~m~', message)
        for i in range(len(lines)):
            logging.info(f'Line #{i}: {lines[i]}')
            try:
                self.emit('incoming', lines[i])
                #self._ws_message_handler(lines[i])
            except Exception as e:
                if re.match(r'^~h~[0-9]+$', lines[i]):
                    self.send_raw(message)
                    continue
                if lines[i]:
                    logging.warn(f'Unable to interpret inbound message: {e}; {lines[i]}', exc_info=True)


    def _on_ws_open_callback(self, ws: WebSocketApp):
        logging.info(f'Established connection to {self.ws_uri}')


    def _on_ws_close_callback(self, ws: WebSocketApp):
        self._reconnect(ws)


    def _on_ws_error_callback(self, ws: WebSocketApp, error: str):
        logging.error(error)
        self._reconnect(ws)


    def _wrap_callback(self, f: callable):
        def wrapped_f(ws, *args, **kwargs):
            if ws is self._ws:
                try:
                    f(ws, *args, **kwargs)
                except Exception as e:
                    raise Exception(f'Error running websocket callback: {e}')
        return wrapped_f
