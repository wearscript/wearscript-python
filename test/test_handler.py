import wearscript
import base64
import argparse
import time

if __name__ == '__main__':
    def callback(ws, **kw):

        def glass_cb(*data):
            command = data[1]
            if command == 'subscribe':
                ws.subscribe(data[2], glass_cb)
            elif command == 'unsubscribe':
                ws.unsubscribe(data[2])
            elif command == 'channelsInternal':
                ws.publish(data[2], ws.channels_internal)
            elif command == 'channelsExternal':
                ws.publish(data[2], ws.channels_external)
            elif command == 'group':
                ws.publish(data[2], ws.group)
            elif command == 'device':
                ws.publish(data[2], ws.device)
            elif command == 'groupDevice':
                ws.publish(data[2], ws.group_device)
            elif command == 'exists':
                ws.publish(data[2], ws.exists(data[3]))
            elif command == 'publish':
                ws.publish(data[2], *data[3:])
            elif command == 'channel':
                ws.publish(data[2], ws.channel(*data[3:]))
            elif command == 'subchannel':
                ws.publish(data[2], ws.subchannel(data[3]))
            elif command == 'ackchannel':
                ws.publish(data[2], ws.ackchannel(data[3]))

                
        ws.subscribe('test', glass_cb)
        for x in range(1000):
            time.sleep(1.5)
            #ws.publish('test', 'data' + str(x % 5))
            print(x)
            
    wearscript.parse(callback, argparse.ArgumentParser())
