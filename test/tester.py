import wearscript
import base64
import os
import random
import argparse
import time
import sys

# Bugs
# Go server didn't send updated device list

# TODO: Test onConnect, onDisconnect

SLEEP = .0

class Device(object):

    def __init__(self, ws, test_channel, group_device):
        self.ws = ws
        self.group_device_this = self.ws.group_device
        self.prefix = self.rand()
        self.response_channel = self.chan()
        self._internal_channels = [test_channel]
        self._external_channels = []  # Ours only
        self._group, self._device = group_device.split(':', 1)
        self._internal_channels_subscription = set([test_channel])  # Reported by remote
        print((self._group, self._device))
        self.expected_responses = []
        self._external_channels.append(self.response_channel)
        self.ws.subscribe(self.response_channel, self.handle)
        time.sleep(SLEEP)

    def _test_channel(self):
        test_channel = random.choice(list(self._internal_channels_subscription.intersection(self._internal_channels)))
        test_channel_parts = test_channel.split(':')
        return ':'.join(test_channel_parts[:random.randint(1, len(test_channel_parts))])

    def rand(self):
        return base64.urlsafe_b64encode(os.urandom(6))

    def chan(self):
        return self._chan_suffix(self.prefix)

    def _chan_suffix(self, prefix, min=1, max=4):
        chan = prefix
        for x in range(random.randint(min, max)):
            chan += ':' + self.rand()
        return chan

    def subscriptions(self, *data):
        assert data[0] == 'subscriptions'
        assert len(data) == 3
        #channels = [x for x in data[2] if x.startswith(self.prefix)]
        #assert set(self._internal_channels + [self.response_channel]) == set(channels)  # BUG: Race here
        assert isinstance(data[1], str)
        assert data[1] == self._group + ':' + self._device
        self._internal_channels_subscription = set(data[2])

    def handle(self, *data):
        try:
            response = self.expected_responses.pop()
            response(*data)
        except:
            name, _, traceback = sys.exc_info()
            print(dir(traceback))
            print('Uncaught Exception: ' + str(name))
            sys.exit(1)

    def publish(self):
        chan = random.choice(self._external_channels)
        data_out = [self._test_channel(), 'publish', chan]
        for x in range(random.randint(0, 5)):
            data_out.append(self.rand())

        def response(*data):
            print((data_out, data))
            assert list(data_out[2:]) == list(data)
        self.expected_responses.append(response)
        self._publish(*data_out)

    def subscribe(self):
        chan = self.chan()
        self._internal_channels.append(chan)
        self._publish(self._test_channel(), 'subscribe', chan)

    def random(self):
        if self.expected_responses:
            return
        random.choice([self.publish, self.subscribe_this, self.unsubscribe_this, self.subscribe, self.unsubscribe, self.channels_internal,
                       self.channels_external, self.group, self.device, self.group_device,
                       self.exists])()

    def subscribe_this(self):
        chan = self.chan()
        self._external_channels.append(chan)
        self.ws.subscribe(chan, self.handle)
        return chan

    def unsubscribe_this(self):
        external_channels = [x for x in self._external_channels if x != self.response_channel]
        if not external_channels:
            return
        removed_channel = random.choice(external_channels)
        self._external_channels = [x for x in self._external_channels if x != removed_channel]
        self.ws.unsubscribe(removed_channel)

    def unsubscribe(self):
        if len(self._internal_channels) > 1:
            random.shuffle(self._internal_channels)
            chan = self._internal_channels.pop()
            self._publish(self._test_channel(), 'unsubscribe', chan)

    def channels_internal(self):
        internal_channels = set(self._internal_channels)
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            print(data)
            channels = set(data[1])
            print((channels, internal_channels))
            assert set(channels).issuperset(internal_channels)
        self.expected_responses.append(response)
        self._publish(self._test_channel(), 'channelsInternal', self.response_channel)

    def channels_external(self):
        external_channels = set(self._external_channels)

        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            print((self.group_device_this, data[1].keys()))
            assert self.group_device_this in data[1].keys()
            channels = [x for x in data[1][self.group_device_this] if x.startswith(self.prefix)]
            print((channels, external_channels))
            assert set(channels) == external_channels
        self.expected_responses.append(response)
        self._publish(self._test_channel(), 'channelsExternal', self.response_channel)

    def group(self):
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            print((self._group, data[1]))
            assert self._group == data[1]
        self.expected_responses.append(response)
        self._publish(self._test_channel(), 'group', self.response_channel)

    def device(self):
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            print((self._device, data[1]))
            assert self._device == data[1]
        self.expected_responses.append(response)
        self._publish(self._test_channel(), 'device', self.response_channel)

    def group_device(self):
        def response(*data):
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert data[1] == self._group + ':' + self._device
        self.expected_responses.append(response)
        self._publish(self._test_channel(), 'groupDevice', self.response_channel)

    def exists(self):
        if random.random() > .5 and self._external_channels:  # True
            chan = self._chan_suffix(random.choice(self._external_channels), 0, 5)
            exists = True
        else:
            chan = self.chan()
            exists = False

        def response(*data):
            print((data, exists, chan))
            assert data[0] == self.response_channel
            assert len(data) == 2
            assert data[1] == exists
        self.expected_responses.append(response)
        self._publish(self._test_channel(), 'exists', self.response_channel, chan)

    def _publish(self, *data):
        print('Publishing: %r' % (data,))
        self.ws.publish(*data)

if __name__ == '__main__':
    def callback(ws, **kw):
        devices = {}

        def subscriptions(*data):
            print(data)
            for x in sorted(data[2]):
                if x.startswith('test:') and data[1] not in devices:
                    print('Making device: %s Channel: %s' % (data[1], x))
                    devices[data[1]] = Device(ws, x, data[1])
                    break
            devices[data[1]].subscriptions(*data)
        ws.subscribe('subscriptions', subscriptions)
        while 1:
            for device in devices.values():
                device.random()
            time.sleep(SLEEP)
    wearscript.parse(callback, argparse.ArgumentParser())
