import gevent.monkey
gevent.monkey.patch_all()
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import os
import websocket
import logging
import msgpack
import random
import sys

class WebSocketException(Exception):
    """Generic error"""


class WearScriptConnection(object):

    def __init__(self, device=None, group='server'):
        self._reset_channels_internal()
        self._reset_external_channels()
        self._group = group
        self._device = device if device else str(random.randint(0, 99999))
        self._group_device = '%s:%s' % (self._group, self._device)
        self.connected = True
        self._lock = gevent.lock.RLock()
        self._loop_greenlet = gevent.spawn(self._loop)
        # TODO(brandyn): Needs onConnect, onDisconnect callbacks

    def _reset_channels_internal(self):
        self._channels_internal = {}

    def _reset_external_channels(self):
        self.device_to_channels = {}  # [device] = list of channels it listens to
        self.external_channels = set()

    def _set_device_channels(self, device, channels):
        self._lock.acquire()
        self.device_to_channels[device] = channels
        self.external_channels = set(sum(self.device_to_channels.values(), []))
        self._lock.release()

    def subscribe(self, channel, callback):
        self._lock.acquire()
        publish = channel not in self._channels_internal
        self._channels_internal[channel] = callback
        channels = list(self._channels_internal)
        self._lock.release()
        if publish:
            self.send('subscriptions', self.group_device, channels)
        return self

    def unsubscribe(self, channel):
        self._lock.acquire()
        publish = channel in self._channels_internal
        del self._channels_internal[channel]
        channels = list(self._channels_internal)
        self._lock.release()
        if publish:
            self.send('subscriptions', self.group_device, channels)
        return self

    def publish(self, channel, *args):
        if not self.connected:
            raise WebSocketException
        if not self.exists(channel):
            return self
        self.send(channel, *args)
        return self

    def exists(self, channel):
        if channel == 'subscriptions':
            return True
        return self._exists(channel, self.external_channels) is not None

    def _exists(self, channel, container):
        channel_cur = None
        parts = channel.split(':')
        for x in parts:
            if channel_cur in container:
                return channel_cur
            if channel_cur is None:
                channel_cur = x
            else:
                channel_cur += ':' + x
        if channel_cur in container:
            return channel_cur

    def channel(self, *args):
        return ':'.join(*args)

    def subchannel(self, *args):
        return ':'.join([self._group, self._device] + list(args))

    def ackchannel(self, channel):
        return ':'.join([channel, 'ACK'])

    @property
    def channels_external(self):
        return self.device_to_channels

    @property
    def channels_internal(self):
        return list(self._channels_internal)

    @property
    def group(self):
        return self._group

    @property
    def device(self):
        return self._device

    @property
    def group_device(self):
        return self._group_device

    def _loop(self):
        while 1:
            try:
                d = self.receive()
            except WebSocketException:
                self.connected = False
                # TODO(brandyn): Here we should reconnect
                print('-------------------Disconnected!')
                break
            print('Got [%s]' % d[0])
            if d[0] == 'subscriptions':
                self._set_device_channels(d[1], d[2])
            try:
                key = self._exists(d[0], self._channels_internal)
                callback = self._channels_internal.get(key)
            except KeyError:
                pass
            if callback:
                try:
                    callback(*d)
                except (SystemExit, WebSocketException):
                    raise
                except:
                    print('Uncaught Exception: ' + str(sys.exc_info()))

    def subscribe_test_handler(self):
        print('Test Subscribing')
        def glass_cb(*data):
            print('Test Data: %r' % (data,))
            command = data[1]
            if command == 'subscribe':
                self.subscribe(data[2], glass_cb)
            elif command == 'unsubscribe':
                self.unsubscribe(data[2])
            elif command == 'channelsInternal':
                self.publish(data[2], self.channels_internal)
            elif command == 'channelsExternal':
                self.publish(data[2], self.channels_external)
            elif command == 'group':
                self.publish(data[2], self.group)
            elif command == 'device':
                self.publish(data[2], self.device)
            elif command == 'groupDevice':
                self.publish(data[2], self.group_device)
            elif command == 'exists':
                self.publish(data[2], self.exists(data[3]))
            elif command == 'publish':
                self.publish(data[2], *data[3:])
            elif command == 'channel':
                self.publish(data[2], self.channel(*data[3:]))
            elif command == 'subchannel':
                self.publish(data[2], self.subchannel(data[3]))
            elif command == 'ackchannel':
                self.publish(data[2], self.ackchannel(data[3]))
        self.subscribe('test:' + self._group_device, glass_cb)


class WebSocketServerConnection(WearScriptConnection):

    def __init__(self, ws):
        super(WebSocketServerConnection, self).__init__()
        self.ws = ws

    def send(self, *args):
        self.ws.send(msgpack.dumps(list(args)), binary=True)

    def receive(self):
        data = self.ws.receive()
        if data is None:
            raise WebSocketException
        return msgpack.loads(data)


class WebSocketClientConnection(WearScriptConnection):

    def __init__(self, ws):
        super(WebSocketClientConnection, self).__init__()
        self.ws = ws

    def send(self, *args):
        self.ws.send(msgpack.dumps(list(args)), opcode=2)

    def receive(self):
        try:
            return msgpack.loads(self.ws.recv())
        except websocket.WebSocketConnectionClosedException:
            raise WebSocketException


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
