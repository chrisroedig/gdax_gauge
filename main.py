import gdax_guage
import threading
from neopixel import *

LED_COUNT      = 32      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest

LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

PRODUCT_ID = 'ETH-USD'

class GDaxLed():
    def __init__(self):
        self.gdax_guage = GDaxGuage(PRODUCT_ID)
        self.strip = Adafruit_NeoPixel(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            LED_STRIP)
        self.run = False
    def start(self):
        self.gdax_guage.start()
        self.run = True
        self.set_pixels_loop()
    def stop(self):
        self.gdax_guage.stop()
        self.run = False
    def set_pixels_loop(self):
        if self.run is not True:
            return
        self.set_pixels()
        threading.Timer(1.00, self.set_pixels_loop).start()
    def set_pixels(self):
        for enumerate(i, color) in self.gdax_guage.combined_pixels():
            self.strip.setPixelColor(i, color)
        self.show()
