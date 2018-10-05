#mocks.py
import numpy as np
import pandas as pd

class DHT22:
    def __init__(self):
        self.sample = 0
        
    def read_retry(self, sensor_type, pin):
        self.sample += 1 
        h,t = (1 / (self.sample * 0.01)) * 1 , (np.cos(self.sample * 0.1) * 50) + 50
        return h, t

class DHT22SampleVals:
    def __init__(self):
        self.sample = 0
        self.data = pd.read_csv('../FirstMeasurement/log.csv', names=['Time', 'Humidity', 'Temperature'])
        self.data['Time'] = pd.to_datetime(self.data['Time'])
        
    def read_retry(self, sensor_type, pin):
        h,t = self.data['Humidity'][self.sample], self.data['Temperature'][self.sample]
        self.sample += 1 
        return h, t

class Relay:
    def __init__(self, pin):
        pass

    def on(self):
        pass

    def off(self):
        pass

class Beeper:
    def __init__(self, pin):
        pass

    def long_beep():
        print('Beep')
        print('\a')