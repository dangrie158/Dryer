from . import mocks, screens, themes, pins
import queue

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

import RPi.GPIO as GPIO

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO.SPI as SPI

from PyEcoder.PyEcoder import Encoder

class App:
    def __init__(self):
        self.process_running = False
        self.theme = themes.LightTheme()
        self.target_humidity = 1.5
        self.max_temperature = 75
        self.max_runtime = datetime.timedelta(hours = 5)
        self.set_eta = None
        self.intermeasurement_delay = 1

class RealApp(App):
    def __init__(self):
        super().__init__()

        backlight = GPIO.PWM(pins.TFT_BL, 1000)
        backlight.start(50)

        self.display = TFT.ILI9341(pins.TFT_DC, rst=pins.TFT_RST, spi=SPI.SpiDev(pins.TFT_SPI_PORT, pins.TFT_SPI_DEVICE, max_speed_hz=64000000))
        TFT_SIZE = (240, 320)

        self.encoder = Encoder(pins.ENC_CLK, pins.ENC_DAT, pins.ENC_BTN)
        self.encoder.on_click(self.current_screen.on_click)
        self.encoder.on_turn(lambda dir: self.current_screen.on_cwturn() if dir else self.current_screen.on_ccwturn())

        self.current_screen = screens.StartScreen(self.display, TFT_SIZE, app=self)

    def run(self):
        self.display.begin()
        threading.Timer(0.033, self.display_loop)

    def invalidate_display(self):
        self.channel.put('invalid')

    def display_loop(self):
        try:
            self.channel.get(block=False)
            self.display.display()
        except queue.Empty:
            pass
        threading.Timer(0.033, self.display_loop)

class MockApp(App):
    def __init__(self):
        super().__init__()

        relay = mocks.Relay(1)
        beeper = mocks.Beeper(1)

        self.read_sensors = partial(mocks.DHT22SampleVals().read_retry, 0, 0)
        self.heater_on = relay.on
        self.heater_off = relay.off
        self.notify_user = beeper.long_beep
        self.intermeasurement_delay = 0.01

        self.channel = queue.Queue()

        #self.display = Image.new('RGBA', (240, 320), (0, 0, 0))
        #TFT_SIZE = self.display.size

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

    def invalidate_display(self):
        self.channel.put('invalid')

    def display_loop(self):
        try:
            self.channel.get(block=False)
            print('display')
            self.root.image = np.rot90(np.asarray(self.display))
            self.im.set_data(self.root.image)
            self.canvas.draw()
        except queue.Empty:
            pass
        self.root.after(33, self.display_loop)