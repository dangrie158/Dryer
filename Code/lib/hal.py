import datetime
import threading

from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

class Encoder:

    LONG_CLICK_TIME = datetime.timedelta(seconds=2)
    MINIMUM_CLICK_TIME = datetime.timedelta(microseconds=100)

    def __init__(self, clk, dt, btn=None, steps=2, debug=False):
        self.clk = clk
        self.dt = dt
        self.btn = btn
        self.steps = steps
        self.delta = 0
        self.debug = debug

        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self._last_clk_state = GPIO.input(clk)

        GPIO.add_event_detect(self.clk, GPIO.FALLING, callback=self._int_callback, bouncetime=1)
        
        if btn is not None:
            if self.debug:
                print('setting up button on pin {}'.format(btn))
            GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.btn, GPIO.BOTH, callback=self._click_int_callback, bouncetime=50)

    def _int_callback(self, channel):
        current_clk_state = GPIO.input(self.clk)
        if self.debug:
            print('interrupt called, new clock state={}'.format(current_clk_state))

        if current_clk_state != self._last_clk_state:
            dt_state = GPIO.input(self.dt)
            if dt_state != current_clk_state and self._click_callback is not None:
                # Clockwise Step
                self.delta +=1

                if self.debug:
                    print('clockwise turn detected')
                
                if self.delta >= self.steps:
                    self._turn_callback(True)
                    self.delta = 0
            else:
                # Counter-Clockwise Step
                self.delta -= 1

                if self.debug:
                    print('counter clockwise turn detected')
                
                if -self.delta >= self.steps: 
                    self._turn_callback(False)
                    self.delta = 0

            self._last_clk_state = current_clk_state

    def _click_int_callback(self, channel):
        if not GPIO.input(self.btn):
            # save the time the button was clicked to detect long clicks
            self.button_clicked_at = datetime.datetime.now()
        else:
            button_released_at = datetime.datetime.now()
            if self.button_clicked_at is not None:
                downtime = button_released_at - self.button_clicked_at 
                if downtime > Encoder.LONG_CLICK_TIME:
                    if self._long_click_callback is not None:
                        self._long_click_callback()
                elif downtime > Encoder.MINIMUM_CLICK_TIME:
                    if self._click_callback is not None:
                        self._click_callback()

    def on_turn(self, callback):
        self._turn_callback = callback
    
    def on_click(self, callback):
        self._click_callback = callback
    
    def on_long_click(self, callback):
        self._long_click_callback = callback

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
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)

class Beeper(Relay):

    LONG_BEEP_DURATIUON = 1.0
    SHORT_BEEP_DURATIUON = 0.1

    def __init__(self, pin):
            return super().__init__(pin)

    def long_beep(self):
        self.on()
        threading.Timer(Beeper.LONG_BEEP_DURATIUON, self.off).start()

    def short_beep(self):
        self.on()
        threading.Timer(Beeper.SHORT_BEEP_DURATIUON, self.off).start()