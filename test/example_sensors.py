import wearscript
import argparse


def callback(ws, **kw):

    def get_image(chan, timestamp, image):
        print('Image[%s] Time[%f] Bytes[%d]' % (chan, timestamp, len(image)))

    def get_sensors(chan, names, samples):
        print('Sensors[%s] Names[%r] Samples[%r]' % (chan, names, samples))

    ws.subscribe('image', get_image)
    ws.subscribe('sensors', get_sensors)
    ws.handler_loop()

wearscript.parse(callback, argparse.ArgumentParser())
