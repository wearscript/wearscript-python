import wearscript
import base64
import os
import random
import argparse
import time
import copy

# Bugs
# Go server didn't send updated device list

# TODO: Test onConnect, onDisconnect

class Device(object):

    def __init__(self, ws, test_channel, group_device):
        self.ws = ws
        self.test_channel = test_channel
        self.group_device_this = 'testerbot:' + self.rand()
        self.prefix = self.rand()
        self.response_channel = self.chan()
        self._internal_channels = []
        self._external_channels = []  # Ours only
        self._group, self._device = group_device.split(':')
        self.expected_responses = []
        self.ws.subscribe(self.response_channel, self.handle)

    def rand(self):
        return base64.urlsafe_b64encode(os.urandom(6))

    def chan(self):
        chan = self.prefix
        for x in range(random.randint(1, 4)):
            chan += ':' + self.rand()
        return chan

    def subscriptions(self, *data):
        assert data[0] == 'subscriptions'
        assert len(data) == 3
        channels = [x for x in data[2] if x.startswith(self.prefix)]
        #assert set(self._internal_channels + [self.response_channel]) == set(channels)  # BUG: Race here
        assert isinstance(data[1], str)
        assert data[1] == self._group + ':' + self._device

    def handle(self, *data):
        response = self.expected_responses.pop()
        response(*data)

    def subscribe(self):
        chan = self.chan()
        self._internal_channels.append(chan)
        self.ws.publish(self.test_channel, 'subscribe', chan)

    def random(self):
        random.choice([self.subscribe_this, self.subscribe, self.unsubscribe, self.channels_internal,
                       self.channels_external, self.group, self.device, self.group_device,
                       self.exists])()

    def subscribe_this(self):
        chan = self.chan()
        self._internal_channels.append(chan)
        self.ws.subscribe(chan, lambda *x: x)
    
    def unsubscribe(self):
        if self._internal_channels:
            random.shuffle(self._internal_channels)
            chan = self._internal_channels.pop()
            self.ws.publish(self.test_channel, 'unsubscribe', chan)

    def channels_internal(self):
        internal_channels = set(self._internal_channels + [self.response_channel])
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            channels = [x for x in data[1][self.group_device_this] if x.startswith(self.prefix)]
            assert set(channels) == internal_channels
        self.expected_responses.append(response)
        self.ws.publish(self.test_channel, 'channelsInternal', self.response_channel)

    def channels_external(self):
        external_channels = set(self._external_channels)
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert self.group_device_this in data[1].keys()
            channels = [x for x in data[1][self.group_device_this] if x.startswith(self.prefix)]
            assert set(channels) == external_channels
        self.expected_responses.append(response)
        self.ws.publish(self.test_channel, 'channelsExternal', self.response_channel)

    def group(self):
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert this.group == data[1]
        self.expected_responses.append(response)
        self.ws.publish(self.test_channel, 'group', self.response_channel)

    def device(self):
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert this.device == data[1]
        self.expected_responses.append(response)
        self.ws.publish(self.test_channel, 'device', self.response_channel)

    def group_device(self):
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert data[1] == self._group + ':' + self._device
        self.expected_responses.append(response)
        self.ws.publish(self.test_channel, 'groupDevice', self.response_channel)

    def exists(self):
        if random.random() > .5 and self._external_channels:  # True
            chan = random.choice(self._external_channels)
            chan = chan.split(':')
            chan = ':'.join(chan[:random.randint(0, len(chan))])
            exists = True
        else:
            chan = self.chan()
            exists = False
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert data[1] == exists
        self.expected_responses.append(response)
        self.ws.publish(self.test_channel, 'exists', self.response_channel, chan)
        

if __name__ == '__main__':
    def callback(ws, **kw):
        devices = {}
        def subscriptions(*data):
            for x in sorted(data[2]):
                if x.startswith('test:') and data[1] not in devices:
                    devices[data[1]] = Device(ws, x, data[1])
                    break
            devices[data[1]].subscriptions(*data)
        ws.subscribe('subscriptions', subscriptions)
        while 1:
            for device in devices.values():
                device.random()
            time.sleep(.1)
            
    wearscript.parse(callback, argparse.ArgumentParser())
