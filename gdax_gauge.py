import gdax_ticker
import gdax_stream
from datetime import datetime
import signal
import sys
import time
import numpy as np
import math

PRODUCT_ID = 'ETH-USD'

class GDaxGuage():
    def __init__(self, product_id, pixel_count=32, price_span=20):
        self.pixel_count = pixel_count
        self.price_span = price_span
        self.stream = gdax_stream.GDaxStream(product_id, buffer_size=1000)
        self.ticker = gdax_ticker.GDaxTicker(product_id)
        self.colors = {
            'open_sell' : np.array([188, 60, 0]),
            'open_buy' : np.array([20, 115,50]),
            'history' : np.array([255, 255, 255])
        }

    def start(self):
        self.stream.start()
        self.ticker.start()

    def stop(self):
        self.stream.close()
        self.ticker.stop()

    @property
    def mid(self):
        return self.ticker.current_price

    @property
    def range(self):
        return (self.mid - self.price_span / 2.0, self.mid + self.price_span / 2.0)

    def pos(self, price):
        return int(math.floor( self.pixel_count * ( price - self.range[0] ) / self.price_span ))

    @property
    def open_sell_pixels(self):
        return self.stream.normalized_histrogram_values('sell', 'open',
            range=self.range, bins=self.pixel_count)
    @property
    def open_buy_pixels(self):
        return self.stream.normalized_histrogram_values('buy', 'open',
            range=self.range, bins=self.pixel_count)
    @property
    def price_history_pixels(self):
        pixels = np.zeros(self.pixel_count)
        for i, p in enumerate(self.ticker.price_history):
            pos = self.pos(p)
            if pos > self.pixel_count -1 or pos < 0:
                continue
            pixels[self.pos(p)] = (10.0 - i) / 10.0
        return pixels

    def combined_pixels(self):
        c_arr = np.transpose(np.array([
            gdax_guage.open_sell_pixels,
            gdax_guage.open_buy_pixels,
            gdax_guage.price_history_pixels
        ]))
        print c_arr
        output = [(0,0,0)] * 32
        for i, channels in enumerate(c_arr):
            for c, amplitude in enumerate(channels):
                if amplitude > 0.0:
                    output[i] = self.pixel_color(amplitude, self.colors.keys()[c])
        return output
    def pixel_color(self, amplitude, color):
        return tuple(np.array(self.colors[color] * amplitude, dtype=int))


if __name__ == '__main__':
    gdax_guage = GDaxGuage(PRODUCT_ID)
    def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        gdax_guage.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    gdax_guage.start()
    while True:
        print gdax_guage.combined_pixels()
        print '\n'
        time.sleep(1)
