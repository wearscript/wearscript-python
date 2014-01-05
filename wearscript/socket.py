import gevent.monkey
gevent.monkey.patch_all()
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import os
import websocket
import logging
import msgpack

class WebSocketException(Exception):
    """Generic error"""


class WebSocketServerConnection(object):

    def __init__(self, ws):
        self.ws = ws

    def send(self, *args):
        self.ws.send(msgpack.dumps(list(args)), binary=True)

    def receive(self):
        data = self.ws.receive()
        if data is None:
            raise WebSocketException
        return msgpack.loads(data)


class WebSocketClientConnection(object):

    def __init__(self, ws):
        self.ws = ws

    def send(self, *args):
        self.ws.send(msgpack.dumps(list(args)), opcode=2)

    def receive(self):
        return msgpack.loads(self.ws.recv())


def websocket_server(callback, websocket_port, **kw):
    
    def websocket_app(environ, start_response):
        logging.info('Glass connected')
        if environ["PATH_INFO"] == '/':
            ws = environ["wsgi.websocket"]
            callback(WebSocketServerConnection(ws), **kw)
            wsgi_server.stop()
    wsgi_server = pywsgi.WSGIServer(("", websocket_port), websocket_app,
                                    handler_class=WebSocketHandler)
    wsgi_server.serve_forever()


def websocket_client_factory(callback, client_endpoint, **kw):
    if not client_endpoint:
        client_endpoint = os.environ['WEARSCRIPT_ENDPOINT']
    callback(WebSocketClientConnection(websocket.create_connection(client_endpoint)), **kw)
