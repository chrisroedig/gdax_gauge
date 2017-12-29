import gdax
import signal
import sys
import time
import numpy as np
from datetime import datetime

PRODUCT_ID = 'ETH-USD'

class GDaxStream(gdax.WebsocketClient):
    def __init__(self, product_id ,events = ['open', 'match'], buffer_size = 100):
        self.product_id = product_id
        self.events = events
        self.buffer_size = buffer_size
        self.init_arrays()
        super(GDaxStream, self).__init__()
    def init_arrays(self):
        self.buffers = {'buy': {}, 'sell': {}}
        for ename in self.events:
            self.buffers['buy'][ename] = np.zeros((self.buffer_size, 2), dtype=float)
            self.buffers['sell'][ename] = np.zeros((self.buffer_size, 2), dtype=float)
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = [self.product_id]
    def on_message(self, msg):
        if msg['type'] not in self.events:
            return
        ts = datetime.strptime(msg['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        ts = (ts - datetime(1970, 1, 1)).total_seconds()
        self.add_event(msg['type'],msg['side'], ts, msg['price'])
    def add_event(self, et, es, ts, price):
        self.buffers[es][et] = np.roll(self.buffers[es][et],1,axis=0)
        self.buffers[es][et][0][0] = ts
        self.buffers[es][et][0][1] = price

    def histogram(self, event_side, event_type, bins=10, range=(0,1000)):
        data = np.transpose(self.buffers[event_side][event_type])[1]
        return np.histogram(data , bins=bins, range=range)
    def normalized_histrogram_values(self, event_side, event_type, **kwargs):
        arr = self.histogram( event_side, event_type, **kwargs)[0]
        arr = np.array(arr, dtype=float)
        return arr / np.max([np.max(arr),1.0])



if __name__ == '__main__':
    gdax_stream = GDaxStream(PRODUCT_ID, buffer_size = 10)
    def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        gdax_stream.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    gdax_stream.start()
    while True:
        print(gdax_stream.histogram('sell','open',bins=32, range=(680,720)))
        time.sleep(1)
