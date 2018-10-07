# screens.py
import datetime
import time
from math import nan
from threading import Thread
import numpy as np

from scipy.interpolate import UnivariateSpline

from . import widgets

class Screen:
    def __init__(self, display, display_size, main_widget, app):
        self.status_bar_height = 15
        self.dialog_margin = 20
        
        self.app = app
        self.display = display
        self.display_size = display_size
        self.widget_size = (0, 0, display_size[0] - self.status_bar_height, display_size[1])
        self.status_bar_size = (display_size[0] - self.status_bar_height, 0, display_size[0], display_size[1])
        self.widget = main_widget(self.widget_size, app.theme)
        self.status_bar = widgets.StatusBar(self.status_bar_size, app.theme)
        
        self.dialog = None
        
    def update_theme(self):
        self.widget.theme = self.app.theme
        self.status_bar.theme = self.app.theme
        if self.dialog is not None:
            self.dialog.theme = self.app.theme
        
    def draw(self):
        # make sure the correct themes are selected
        self.update_theme()
        
        self.status_bar.draw(self.display)
        self.widget.draw(self.display)
        if self.dialog is not None:
            self.dialog.draw(self.display)
            
        self.app.invalidate_display()
        self.app.wait_for_display()
            
    def on_cwturn(self):
        pass
    
    def on_ccwturn(self):
        pass
    
    def on_click(self):
        pass
    
    def switch_screen(self, new_screen):
        self.app.current_screen = new_screen(self.display, self.display_size, app=self.app)
        self.app.current_screen.draw()

    def create_dialog(self, title, left_btn, right_btn=None):
        self.dialog = widgets.Dialog((self.dialog_margin, 
                                        self.dialog_margin, 
                                        self.display_size[0] - self.status_bar_height - self.dialog_margin, 
                                        self.display_size[1] - self.dialog_margin), 
                                        self.app.theme)
        self.dialog.title = title
        self.dialog.buttons['left'] = left_btn
        self.dialog.buttons['right'] = right_btn
        

class StartScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, main_widget=widgets.StartWidget)
                       
    def on_click(self):
        self.switch_screen(MainMenuScreen)
        
class MainMenuScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, main_widget=widgets.MenuWidget)
        
        self.widget.add_item('Target Humidity', 'resources/icons/humidity.png')
        self.widget.add_item('max. Temperature', 'resources/icons/temperature.png')
        self.widget.add_item('max. Runtime', 'resources/icons/time.png')
        self.widget.add_item('ETA', 'resources/icons/targettime.png')
        self.widget.add_item('Start Process', 'resources/icons/start.png', '>')
        
        self.display_limits()
        
        self.editing_item = -1
        
        
    def display_limits(self):
        self.widget.menu_items[0][2] = '{:03.1f}%'.format(self.app.target_humidity)
        self.widget.menu_items[1][2] = '{:2d}°C'.format(self.app.max_temperature)
        self.widget.menu_items[2][2] = '{}'.format(self.app.max_runtime)
        self.widget.menu_items[3][2] = '{:%H:%M}'.format(self.app.set_eta) if self.app.set_eta is not None else 'ASAP'
                       
    def on_click(self):
        if self.editing_item == -1:
            if self.widget.selected_item == 4:
                self.switch_screen(ProgressScreen)
                return
            else:
                self.editing_item = self.widget.selected_item
                self.widget.edit_mode = True
        else:
            self.widget.edit_mode = False
            self.editing_item = -1

        self.draw()
        
    def on_cwturn(self):
        if self.editing_item == -1:
            self.widget.scroll_down()
        elif self.editing_item == 0:
            # target humidity selected, increase by 0.5% step
            if self.app.target_humidity < 50:
                self.app.target_humidity += 0.5
        elif self.editing_item == 1:
            # max temp selected, increase by 5°C
            if self.app.max_temperature < 100:
                self.app.max_temperature += 5
        elif self.editing_item == 2:
            # max runtime selected, increase by 15 min
            if self.app.max_runtime < datetime.timedelta(hours=23, minutes=45):
                if self.app.set_eta is not None:
                    eta_offset = (self.app.set_eta - datetime.datetime.now()) - self.app.max_runtime
                    self.app.set_eta = datetime.datetime.now() + (self.app.max_runtime + datetime.timedelta(minutes=15)) + eta_offset

                self.app.max_runtime += datetime.timedelta(minutes=15)
        elif self.editing_item == 3:
            # eta selected
            if self.app.set_eta is None:
                # if eta was none, set to a datetime object 15min in the future
                self.app.set_eta = datetime.datetime.now() + self.app.max_runtime + datetime.timedelta(minutes=15)
            else:
                # limit the start offset to the next 24h
                if self.app.set_eta + datetime.timedelta(minutes=15) < datetime.datetime.now() + datetime.timedelta(days=1):
                    self.app.set_eta += datetime.timedelta(minutes=15)
            
        self.display_limits()
        self.draw()
        
    def on_ccwturn(self):
        if self.editing_item == -1:
            self.widget.scroll_up()
        elif self.editing_item == 0:
            # target humidity selected, decrease by 0.5% step
            if self.app.target_humidity > 0.5:
                self.app.target_humidity -= 0.5
        elif self.editing_item == 1:
            # max temp selected, decrease by 5°C
            if self.app.max_temperature > 50:
                self.app.max_temperature -= 5
        elif self.editing_item == 2:
            # max runtime selected, decrease by 15 min
            if self.app.max_runtime > datetime.timedelta(minutes=15):
                if self.app.set_eta is not None:
                    eta_offset = (self.app.set_eta - datetime.datetime.now()) - self.app.max_runtime
                    self.app.set_eta = datetime.datetime.now() + (self.app.max_runtime - datetime.timedelta(minutes=15)) + eta_offset

                self.app.max_runtime -= datetime.timedelta(minutes=15)
        elif self.editing_item == 3:
            # eta selected
            if self.app.set_eta is not None and (self.app.set_eta - self.app.max_runtime - datetime.timedelta(minutes=15)) < datetime.datetime.now():
                # eta was at minimum, set to None
                self.app.set_eta = None
            elif self.app.set_eta is not None:
                # decrease set eta by 15 minutes
                self.app.set_eta -= datetime.timedelta(minutes=15)
            
        self.display_limits()
        self.draw()
        
class ProgressScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, main_widget=widgets.ProgressWidget)
        
        self.app.process_running = False
        self.is_waiting = False
        self.process_finished = False
        self.widget.set_graphdata([datetime.datetime.now()], [nan], [nan])
        self.widget.set_targets(humidity=self.app.target_humidity, temperature=self.app.max_temperature)
        self.temperatures = []
        self.humidities = []
        self.timestamps = []

        # minimum number of sensor samples to collect before calculating an ETA
        self.minimum_eta_samples = 100

        # sometimes the first few readings from the DHT are too low, 
        # take a minimun number of samples before ending the process
        self.minimum_humid_samples = 10
        
        if self.app.set_eta is None:
            # start the process immediately
            self.start()
        else:
            # display a dialog how long the process will wait before starting
            self.create_dialog('Waiting...', 'Cancel', 'Start')
            self.draw()
            self.is_waiting = True

        Thread(target=self.screen_updater).start()
        
    def on_click(self):
        if self.is_waiting:
            if self.dialog.selected_button == 'left':
                self.is_waiting = False
                self.stop('Process canceled')
            else:
                self.is_waiting = False
                self.dialog = None
                self.start()
                self.draw()

        if self.process_finished: 
            # process was finished, restart the app
            self.switch_screen(StartScreen)
            return

        if not self.is_waiting and not self.app.process_running:
            # process stopped, but dont restart the app yet, just hide the dialog
            self.process_finished = True
            self.dialog = None
            self.draw()

        if self.dialog is None and self.app.process_running:
            # display a cancel dialog if the progress is running
            self.create_dialog('Cancel process?', 'No', 'Yes')
            self.draw()
        elif self.dialog is not None and self.app.process_running:
            # when the dialog is already displayed, handle the choice
            if self.dialog.selected_button == 'left':
                # Hide the dialog, continue Process
                self.dialog = None
                self.draw()
            else:
                self.stop('Process canceled')

    def on_cwturn(self):
        if self.dialog is not None:
            self.dialog.select_next()
            self.draw()

    def on_ccwturn(self):
        if self.dialog is not None:
            self.dialog.select_next()
            self.draw()
            
    def start(self):
        self.app.process_running = True
        self.is_waiting = False
        self.app.heater_on()
        self.status_bar.status['power'] = True
        Thread(target=self.sensor_reader).start()

    def stop(self, reason):
        self.app.process_running = False
        self.is_waiting = False
        self.app.heater_off()
        self.status_bar.status['power'] = False
        self.create_dialog(reason, 'OK')
        self.draw()
        self.app.notify_user()

    def screen_updater(self):
        while self.app.process_running or self.is_waiting:
            time.sleep(1)
            if len(self.timestamps) > 0:
                self.timestamps[-1] = datetime.datetime.now()
                self.widget.set_graphdata(self.timestamps, self.humidities, self.temperatures)

            if self.is_waiting:
                time_left = (self.app.set_eta.replace(microsecond=0) - datetime.datetime.now().replace(microsecond=0)) - self.app.max_runtime
                self.dialog.title = "Waiting {}...".format(time_left)

                if time_left <= datetime.timedelta(seconds = 0):
                    self.dialog = None
                    self.is_waiting = False
                    self.app.notify_user()
                    self.start()
            
            self.draw()

    def sensor_reader(self):
        while self.app.process_running:
            self.make_sensor_reading()
            self.widget.set_graphdata(self.timestamps, self.humidities, self.temperatures)
            time.sleep(self.app.intermeasurement_delay)

            if len(self.timestamps) > self.minimum_eta_samples:
                eta = self.get_eta()
                targets = {
                    'time': eta, 
                    'humidity': self.app.target_humidity, 
                    'temperature': self.app.max_temperature
                }
                self.widget.set_targets(**targets)
    
    def make_sensor_reading(self):
        humid, temp = self.app.read_sensors()
        self.temperatures.append(temp)
        self.humidities.append(humid)
        self.timestamps.append(datetime.datetime.now())

        if temp > self.app.max_temperature:
            self.stop('Overtemperature!')

        if len(self.humidities) > self.minimum_humid_samples and humid <= self.app.target_humidity:
            self.stop('Process Finished')

        if self.app.max_runtime <= (self.timestamps[-1] - self.timestamps[0]):
            self.stop('Process Timeout')


    def get_eta(self):
        # fit a 3rd order polynomial to the data
        timestamps = [(x - self.timestamps[0]).total_seconds() for x in self.timestamps]
        # sample weight is less for older samples
        weights = [x ** 2 for x in range(len(timestamps))]

        coeffs = np.polyfit(timestamps, self.humidities, w=weights, deg=3)
        poly = np.poly1d(coeffs)
        # find where the polynomial intersects the target humidity
        y0 = self.app.target_humidity
        x0 = (poly - y0).roots
        # filter complex solutions
        x0 = x0[np.isreal(x0)]
        if len(x0) > 0:
            eta = datetime.timedelta(seconds=int(x0[0])) - (self.timestamps[-1].replace(microsecond=0) - self.timestamps[0].replace(microsecond=0))
            if eta.total_seconds() > 0:
                return eta

        return None