import wearscript
import argparse
import time


if __name__ == '__main__':
    def callback(ws, *args):
        ws.subscribe_test_handler()
        while 1:
            time.sleep(1)
    wearscript.parse(callback, argparse.ArgumentParser())
