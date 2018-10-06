from . import screens, themes, pins, hal
from .mocks import Relay as MockRelay, Beeper as MockBeeper, DHT22SampleVals as MockDHT22

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as Tk
from PIL import Image
import numpy as np

from functools import partial
import queue
import math
import datetime
import threading
import time
import queue
import atexit

import RPi.GPIO as GPIO

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO.SPI as SPI
import Adafruit_DHT

class App:
    def __init__(self):
        self.process_running = False
        self.theme = themes.LightTheme()
        self.target_humidity = 4
        self.max_temperature = 75
        self.max_runtime = datetime.timedelta(hours = 6)
        self.set_eta = None
        self.intermeasurement_delay = 1

        self.channel = queue.Queue()

    def invalidate_display(self):
        self.channel.put('invalid')

class RealApp(App):
    def __init__(self):
        super().__init__()

        GPIO.setmode(GPIO.BCM)

        self.backlight = hal.Relay(pins.TFT_BL)
        self.backlight.on()

        self.display = TFT.ILI9341(pins.TFT_DC, rst=pins.TFT_RST, spi=SPI.SpiDev(pins.TFT_SPI_PORT, pins.TFT_SPI_DEVICE, max_speed_hz=64000000))
        TFT_SIZE = (240, 320)
        self.display.begin()

        self.current_screen = screens.StartScreen(self.display, TFT_SIZE, app=self)

        self.encoder = hal.Encoder(pins.ENC_CLK, pins.ENC_DAT, pins.ENC_BTN)
                
        # The Unit has two relays to switch without potential no matter the plug orientation
        self.relay1 = hal.Relay(pins.RELAY_1)
        self.relay2 = hal.Relay(pins.RELAY_2)
        # Make sure heater is initially off
        self.switch_heater(False)

        self.beeper = hal.Beeper(pins.BEEPER)

        def cleanup():
            self.switch_heater(False)
            self.beeper.off()
            self.backlight.off()
            self.display.clear()
            GPIO.cleanup()
        atexit.register(cleanup)

        def click():
            self.beeper.short_beep()
            self.current_screen.on_click()

        def turn(dir):
            self.beeper.short_beep()
            if dir:
                self.current_screen.on_ccwturn()  
            else:
                 self.current_screen.on_cwturn()

        self.encoder.on_click(click)
        self.encoder.on_turn(turn)
        self.encoder.on_long_click(lambda: self.toggle_theme())

        self.read_sensors = partial(Adafruit_DHT.read_retry, Adafruit_DHT.DHT22, pins.DHT22)
        self.heater_on = partial(self.switch_heater, True)
        self.heater_off = partial(self.switch_heater, False)
        self.notify_user = self.beeper.long_beep
        self.intermeasurement_delay = 0.1

        self.current_screen.draw()

    def toggle_theme(self):
        self.theme = themes.DarkTheme() if type(self.theme) == themes.LightTheme else themes.LightTheme()
        self.current_screen.draw()

    def switch_heater(self, state):
        if state:
            self.relay1.on()
            self.relay2.on()
        else:
            self.relay1.off()
            self.relay2.off()

    def run(self):
        threading.Timer(0.033, self.display_loop).start()
        while True:
            time.sleep(1)

    def display_loop(self):
        try:
            self.channel.get(block=True)
            self.display.display()
        except queue.Empty:
            pass
        threading.Timer(0.033, self.display_loop).start()

class MockApp(App):
    def __init__(self):
        super().__init__()

        relay = MockRelay(1)
        beeper = MockBeeper(1)

        self.read_sensors = partial(MockDHT22().read_retry, 0, 0)
        self.heater_on = relay.on
        self.heater_off = relay.off
        self.notify_user = beeper.long_beep
        self.intermeasurement_delay = 0.01

        self.display = Image.new('RGBA', (240, 320), (0, 0, 0))
        TFT_SIZE = self.display.size

        self.root = Tk.Tk()
        self.root.wm_title("Smart Dry Mock")
        self.root.image = np.rot90(np.asarray(self.display))
        fig = plt.figure(figsize = (5,5))
        self.im = plt.imshow(self.root.image)
        ax = plt.gca()
        ax.set_xticklabels([]) 
        ax.set_yticklabels([])

        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        Tk.Button(self.root, text="CW", command=self.cw_clicked).pack()
        Tk.Button(self.root, text="CCW", command=self.ccw_clicked).pack()
        Tk.Button(self.root, text="Click", command=self.btn_clicked).pack()
        Tk.Button(self.root, text="longpress", command=self.longclick_clicked).pack()

        self.current_screen.draw()

    def cw_clicked(self):
        self.current_screen.on_cwturn()
        
    def ccw_clicked(self):
        self.current_screen.on_ccwturn()
        
    def btn_clicked(self):
        self.current_screen.on_click()
        
    def longclick_clicked(self):
        self.theme = themes.DarkTheme() if type(self.theme) == themes.LightTheme else themes.LightTheme()

    def run(self):
        self.root.after(33, self.display_loop)
        self.root.mainloop()

    def display_loop(self):
        try:
            self.channel.get(block=False)
            self.root.image = np.rot90(np.asarray(self.display))
            self.im.set_data(self.root.image)
            self.canvas.draw()
        except queue.Empty:
            pass
        self.root.after(33, self.display_loop)