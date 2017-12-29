import gdax
import time
import signal
import sys
import threading
import numpy as np

PRODUCT_ID = 'ETH-USD'

class GDaxTicker():
    def __init__(self, product_id):
        self.client = gdax.PublicClient()
        self.product_id = product_id
        self.run = False
        self.price_history = np.zeros(10, dtype=float)
    @property
    def current_price(self):
        return self.price_history[0]
    def get_ticker(self):
        self.data = self.client.get_product_ticker(product_id=self.product_id)
        if float(self.data['price']) != self.current_price:
            self.price_history = np.roll(self.price_history, 1)
            self.price_history[0] = self.data['price']
    def start(self):
        self.run = True
        self.start_ticker()
    def stop(self):
        self.run = False
    def start_ticker(self):
        if self.run is not True:
            return
        self.get_ticker()
        threading.Timer(10.00, self.start_ticker).start()

if __name__ == '__main__':
    gdax_ticker = GDaxTicker(PRODUCT_ID)
    def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        gdax_ticker.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    gdax_ticker.start()
    while True:
        print(gdax_ticker.price_history)
        time.sleep(30)
