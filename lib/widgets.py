# widgets.py
from PIL import Image, ImageDraw
import datetime
from math import isnan

from .utils import load_image, draw_rotated_text, paste_image, draw_rotated_text_centered

class Widget:
    def __init__(self, xy, theme):
        self.xy = xy
        self.theme = theme
        
    @property
    def width(self):
        return self.xy[2] - self.xy[0]
    
    @property
    def height(self):
        return self.xy[3] - self.xy[1]
    
    def draw(self, image):
        raise NotImplementedError('Your Screen should Override the draw() Method')

class StatusBar(Widget):
    def __init__(self, xy, theme):
        super().__init__(xy, theme)
        
        self.status = {
            'power': False
        }
        
        self.power_icon = load_image('resources/icons/power.png', theme)
        
    def draw(self, image):
        context = image.draw(image)
        
        context.rectangle(self.xy, fill=self.theme.COLOR_BACKGROUND)
        
        margin_x = 2
        margin_y = 8
        
        # draw the power status icon
        if self.status['power']:
            paste_image(image, self.power_icon, (self.xy[0] + int(margin_x / 2), self.xy[1] + margin_y), self.theme)
        
        # draw the current time
        current_time = '{:%H:%M}'.format(datetime.datetime.now())
        time_size = context.textsize(current_time, self.theme.FONT_REGULAR_BOLD)
        draw_rotated_text(image, current_time, (self.xy[0] + margin_x, (self.height) / 2 - time_size[0]/ 2), -90, self.theme.FONT_REGULAR_BOLD, self.theme.COLOR_PRIMARY)
        
class Graph(Widget):
    def __init__(self, xy, theme):
        super().__init__(xy, theme)
        self.series = {'left': ([], theme.COLOR_HUMIDITY), 
                        'right': ([], theme.COLOR_TEMPERATURE)}
        self.legends = {'left': (0,0, theme.COLOR_HUMIDITY), 
                        'right': (0,0, theme.COLOR_TEMPERATURE)}

    
    def set_series(self, side, series, color):
        if side not in ('left', 'right'):
            raise ValueError('Only "left" or "right" allowed for parameter side')
        self.series[side] = ((series, color))
        
        lower_lim = min(series)
        if isnan(lower_lim):
            lower_lim = 'n/a'
            
        upper_lim = max(series)
        if isnan(upper_lim):
            upper_lim = 'n/a'
        self.legends[side] = (lower_lim, upper_lim, color)
        
    def set_yaxis(self, data):
        self.yaxis = data 
    
    def draw(self, image):
        context = image.draw(image)
        # Draw a background for the graph
        context.rectangle(self.xy, fill=self.theme.COLOR_BACKGROUND)
        
        legend_width = 10
        legend_width_top = legend_width / 2
        legend_width_bottom = 0
        legend_width_lr = legend_width * 3
        legend_tick_length = legend_width / 4
        
        legend_margin_x = legend_width_bottom + 1
        legend_margin_y = legend_width_lr + 1
        
        line_width = 2
        
        legend_color = self.theme.COLOR_PRIMARY
        
        legend_font = self.theme.FONT_LEGEND
        
        # draw the data lines
        for line_data, line_color in self.series.values():
            x_values = line_data
            y_values = list(range(len(self.yaxis)))
            
            min_x, max_x = min(x_values), max(x_values)
            min_y, max_y = 0, len(y_values)
            
            if (max_x - min_x) != 0:
                scale_x = (self.width - (legend_margin_x + legend_width_top)) / (max_x - min_x)
            else:
                scale_x = 1
                
            if (max_y - min_y) != 0:
                scale_y = (self.height - (legend_margin_y * 2)) / (max_y - min_y)
            else:
                scale_y = 1
            
            offset_x = self.xy[0] + legend_margin_x - (min_x * scale_x)
            offset_y = self.xy[1] + legend_margin_y
            
            line = [(xy[1] * scale_x + offset_x, xy[0] * scale_y + offset_y) for xy in zip(y_values, x_values)]
            context.line(line, fill=line_color, width=line_width)
            
        # draw the legend lines
        # left
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + legend_width_lr, 
                      self.xy[0] + self.width - legend_width_top, self.xy[1] + legend_width_lr), 
                     fill=legend_color)
        # right
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + self.height - legend_width_lr, 
                      self.xy[0] + self.width - legend_width_top, self.xy[1] + self.height - legend_width_lr), 
                     fill=legend_color)
        # bottom
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + legend_width_lr, 
                      self.xy[0] + legend_width_bottom, self.xy[1] + self.height - legend_width_lr), 
                     fill=legend_color)
        
        # draw the ticks
        # left bottom
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + legend_width_lr, 
                      self.xy[0] + legend_width_bottom, self.xy[1] + legend_width_lr - legend_tick_length), 
                     fill=legend_color)
        # left top
        context.line((self.xy[0] + self.width - legend_width_top, self.xy[1] + legend_width_lr, 
                      self.xy[0] + self.width - legend_width_top, self.xy[1] + legend_width_lr - legend_tick_length), 
                     fill=legend_color)
        
        # right bottom
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + self.height - legend_width_lr, 
                      self.xy[0] + legend_width_bottom, self.xy[1] + self.height - legend_width_lr + legend_tick_length), 
                     fill=legend_color)
        # right top
        context.line((self.xy[0] + self.width - legend_width_top, self.xy[1] + self.height - legend_width_lr, 
                      self.xy[0] + self.width - legend_width_top, self.xy[1] + self.height - legend_width_lr + legend_tick_length),
                     fill=legend_color)
        
        # bottom start
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + legend_width_lr, 
                      self.xy[0] + legend_width_bottom - legend_tick_length, self.xy[1] + legend_width_lr, ), 
                     fill=legend_color)
        # bottom end
        context.line((self.xy[0] + legend_width_bottom, self.xy[1] + self.height - legend_width_lr, 
                      self.xy[0] + legend_width_bottom - legend_tick_length, self.xy[1] + self.height - legend_width_lr),
                     fill=legend_color)
        
        # draw the legend texts
        # left lower bound
        llb = '{:03.1f}'.format(self.legends['left'][0])
        llb_size = context.textsize(llb, font=legend_font)
        draw_rotated_text(image, llb, (self.xy[0] + legend_width_bottom - (llb_size[1] / 2), self.xy[1] + legend_width_lr - legend_tick_length - llb_size[0]), angle=-90, font=legend_font, fill=self.legends['left'][2])

        # left upper bound
        lub = '{:03.1f}'.format(self.legends['left'][1])
        lub_size = context.textsize(lub, font=legend_font)
        draw_rotated_text(image, lub, (self.xy[0] + self.width - legend_width_top - (lub_size[1] / 2), self.xy[1] + legend_width_lr - legend_tick_length - lub_size[0]), angle=-90, font=legend_font, fill=self.legends['left'][2])

        # right lower bound
        rlb = '{:03.1f}'.format(self.legends['right'][0])
        rlb_size = context.textsize(rlb, font=legend_font)
        draw_rotated_text(image, rlb, (self.xy[0] + legend_width_bottom - (rlb_size[1] / 2), self.xy[1] + self.height - legend_width_lr + legend_tick_length + 5), angle=-90, font=legend_font, fill=self.legends['right'][2])

        # right upper bound
        rub = '{:03.1f}'.format(self.legends['right'][1])
        rub_size = context.textsize(rub, font=legend_font)
        draw_rotated_text(image, rub, (self.xy[0] + self.width - legend_width_top - (rub_size[1] / 2), self.xy[1] + self.height - legend_width_lr + legend_tick_length + 5), angle=-90, font=legend_font, fill=self.legends['right'][2])
        
class ProgressWidget(Widget):
    def __init__(self, xy, theme):
        super().__init__(xy, theme)
        
        self.graph = Graph((self.xy[0] + 50, self.xy[1], self.xy[2], self.xy[3]), theme=self.theme)
        
        self.target_time = None
        self.target_humidity = None
        self.target_temperature = None
        
    def set_graphdata(self, timestamps, humidity, temperature):
        # make sure the timestamps only have 1 second resolution
        self.timestamps = [x.replace(microsecond=0) for x in timestamps]
        self.humidity = humidity
        self.temperature = temperature

        self.graph.set_series('left', self.humidity, self.theme.COLOR_HUMIDITY)
        self.graph.set_series('right', self.temperature, self.theme.COLOR_TEMPERATURE)
        self.graph.set_yaxis(self.timestamps)
        
    def set_targets(self, time=None, humidity=None, temperature=None):
        self.target_time = time
        self.target_humidity = humidity
        self.target_temperature = temperature
        
    def draw(self, image):
        context = image.draw(image)
        self.graph.theme = self.theme
        
        context.rectangle(self.xy, fill=self.theme.COLOR_BACKGROUND)
        
        # draw latest values as text
        text_y = 15
        time_x = (self.height) / 2
        humid_x = time_x - 110
        temp_x = time_x + 110
        
        offset_limit_text = -13
        offset_title_text = 15
        
        draw_rotated_text_centered(image, "RH:", (text_y + offset_title_text, humid_x), self.theme.FONT_REGULAR, self.theme.COLOR_HUMIDITY)
        
        humidity_string = 'n/a' if isnan(self.humidity[-1]) else '{:03.1f}%'.format(self.humidity[-1])
        draw_rotated_text_centered(image, humidity_string, (text_y, humid_x), self.theme.FONT_BIG, self.theme.COLOR_HUMIDITY)
        
        if self.target_humidity is not None:
            targethumidity_string = 'target: {:03.1f}%'.format(self.target_humidity)
            draw_rotated_text_centered(image, targethumidity_string, (text_y + offset_limit_text, humid_x), self.theme.FONT_SMALL, self.theme.COLOR_HUMIDITY)
        
        draw_rotated_text_centered(image, "Temp:", (text_y + offset_title_text, temp_x), self.theme.FONT_REGULAR, self.theme.COLOR_TEMPERATURE)
        temp_string = 'n/a' if isnan(self.temperature[-1]) else '{:03.1f}°C'.format(self.temperature[-1])
        draw_rotated_text_centered(image, temp_string, (text_y, temp_x), self.theme.FONT_BIG, self.theme.COLOR_TEMPERATURE)
        if self.target_temperature is not None:
            targettemp_string = 'max: {:03.1f}°C'.format(self.target_temperature)
            draw_rotated_text_centered(image, targettemp_string, (text_y + offset_limit_text, temp_x), self.theme.FONT_SMALL, self.theme.COLOR_TEMPERATURE)
        
        draw_rotated_text_centered(image, "Runtime:", (text_y + offset_title_text, time_x), self.theme.FONT_REGULAR, self.theme.COLOR_PRIMARY)
        temp_string = '{}'.format(self.timestamps[-1] - self.timestamps[0])
        draw_rotated_text_centered(image, temp_string, (text_y, time_x), self.theme.FONT_BIG, self.theme.COLOR_PRIMARY)
        if self.target_time is not None:
            targettime_string = 'ETA: {}'.format(self.target_time)
            draw_rotated_text_centered(image, targettime_string, (text_y + offset_limit_text, time_x), self.theme.FONT_SMALL, self.theme.COLOR_PRIMARY)
        
        self.graph.draw(image)
        
class MenuWidget(Widget):
    def __init__(self, xy, theme):
        super().__init__(xy, theme)
        
        self.menu_items = []
        self.selected_item = 0
        self.scroll_offset = 0
        
        
        self.item_height = 45
        
        #whether or not the selected item is in edit mode
        self.edit_mode = False
        
        # calculate how many items will fit on the screen given the size
        self.items_on_screen = int(self.width / self.item_height)
        
    def add_item(self, title, icon_file=None, end=None):
        icon = load_image(icon_file, self.theme) if icon_file is not None else None
            
        self.menu_items.append([title, icon, end])
        
    def scroll_down(self):
        if self.selected_item < len(self.menu_items) - 1:
            self.selected_item += 1
            if self.selected_item - self.scroll_offset >= self.items_on_screen:
                self.scroll_offset += 1
            
    def scroll_up(self):
        if self.selected_item > 0:
            self.selected_item -= 1
            if self.selected_item < self.scroll_offset:
                self.scroll_offset -= 1
        
    def draw(self, image):
        context = image.draw(image)
        
        context.rectangle(self.xy, fill=self.theme.COLOR_BACKGROUND)
        margin_x = 8
        
        
        for num, menu_item in enumerate(self.menu_items[self.scroll_offset : self.scroll_offset + self.items_on_screen]):
            title, icon, end = menu_item
            item_index = num + self.scroll_offset
            
            # draw the selector for the currently selected icon
            if item_index == self.selected_item:
                selection_xy = (self.xy[2] - self.item_height * (num + 1),
                                self.xy[1],
                                self.xy[2] - self.item_height * num,
                                self.xy[3])
                
                selection_color = self.theme.COLOR_EDIT if self.edit_mode else self.theme.COLOR_SELECTION
                context.rectangle(selection_xy, fill=selection_color)
            
            # draw icon
            if icon is not None:
                icon_x, icon_y = int(self.xy[2] - self.item_height * num - self.item_height / 2 - icon.height / 2), self.xy[1] + margin_x
                paste_image(image, icon, (icon_x, icon_y), self.theme)
        
            # draw title
            title_size = context.textsize(title, font=self.theme.FONT_BIG)
            title_x, title_y = self.xy[2] - (self.item_height * num) - self.item_height / 2 - title_size[1] / 2, self.xy[1] + icon.width + margin_x * 2
            draw_rotated_text(image, title, (title_x, title_y), angle=-90, font=self.theme.FONT_BIG, fill=self.theme.COLOR_PRIMARY)
        
            # draw the end text
            if end is not None:
                end_size = context.textsize(end, font=self.theme.FONT_BIG)
                title_x, title_y = self.xy[2] - (self.item_height * num) - self.item_height / 2 - end_size[1] / 2, self.xy[3] - end_size[0] - margin_x
                draw_rotated_text(image, end, (title_x, title_y), angle=-90, font=self.theme.FONT_BIG, fill=self.theme.COLOR_PRIMARY)
            
class StartWidget(Widget):
    def __init__(self, xy, theme):
        super().__init__(xy, theme)
        
        self.logo = Image.open('resources/icons/logo.png').rotate(-90).convert('RGBA')
        self.start_icon = load_image('resources/icons/start_small.png', theme)
                
    def draw(self, image):
        context = image.draw(image)
        
        context.rectangle(self.xy, fill=self.theme.COLOR_BACKGROUND)
        
        # draw the logo
        logo_x, logo_y = int(self.xy[0] + self.width / 2 - self.logo.width / 2), int(self.xy[1] + self.height / 2 - self.logo.height/2)
        paste_image(image, self.logo, (logo_x, logo_y), self.theme)
        
        # draw the title
        draw_rotated_text_centered(image, "Smart Dryer", (logo_x + self.logo.width + 20, self.xy[1] + self.height / 2), self.theme.FONT_BIG, self.theme.COLOR_PRIMARY)
        
        # draw the start button
        icon_margin = 30
        logo_offset = 40
        button_text = "Start"
        button_text_size = context.textsize(button_text, self.theme.FONT_BIG)
        
        
        selection_width, selection_height = 25, 120
        selection_xy = (logo_x - logo_offset + button_text_size[1] / 2 - selection_width / 2 - 3,
                        self.xy[1] + self.height / 2 - selection_height / 2,
                        logo_x - logo_offset + button_text_size[1] / 2 + selection_width / 2,
                        self.xy[1] + self.height / 2 + selection_height / 2)
        context.rectangle(selection_xy, fill=self.theme.COLOR_SELECTION)
        
        draw_rotated_text_centered(image, button_text, (logo_x - logo_offset, (self.xy[1] + self.height / 2) - (icon_margin / 2)), self.theme.FONT_BIG, self.theme.COLOR_PRIMARY)
        paste_image(image, self.start_icon, (logo_x - logo_offset - 2, int((self.xy[1] + self.height / 2) + (icon_margin / 2) + self.start_icon.width / 2)), self.theme)
         
class Dialog(Widget):
    def __init__(self, xy, theme):
        super().__init__(xy, theme)
        
        self.title = ''
        self.buttons = {
            'left': '',
            'right': None
        }
        
        self.selected_button = 'left'
        
    def select_next(self):
        if self.buttons['right'] is None:
            return
        
        self.selected_button = 'left' if self.selected_button == 'right' else 'right'
        
    def draw(self, image):
        context = image.draw(image)
        
        context.rectangle(self.xy, fill=self.theme.COLOR_BACKGROUND, outline=self.theme.COLOR_PRIMARY)
        
        dialog_margin = 30
        selection_size = 100, 26
        button_distance = 60
        title_font = self.theme.FONT_BIG
        button_font = self.theme.FONT_REGULAR_BOLD
        
        # draw the title
        title_size = context.textsize(self.title, title_font)
        draw_rotated_text_centered(image, self.title, (self.xy[2] - self.xy[0] - dialog_margin, self.xy[1] + self.height / 2), title_font, self.theme.COLOR_PRIMARY)
        
        # draw the left button
        button_l_text_size = context.textsize(self.buttons['left'], button_font)
        # by default the button is centered
        button_l_x = self.xy[0] + dialog_margin + button_l_text_size[1]
        button_l_y = self.xy[1] + self.height / 2
        button_center_x = button_l_x + button_l_text_size[1] / 2
        
        # move button to left if another button is defined
        if self.buttons['right'] is not None:
            button_l_y -= button_distance
            
        
        btnl_fill = self.theme.COLOR_SELECTION if self.selected_button == 'left' else self.theme.COLOR_BACKGROUND
        buttonl_selection = (button_center_x - selection_size[1] / 2,
                             button_l_y - selection_size[0] / 2, 
                             button_center_x + selection_size[1] / 2,
                             button_l_y + selection_size[0] / 2)
        context.rectangle(buttonl_selection, fill=btnl_fill, outline=self.theme.COLOR_PRIMARY)
            
        draw_rotated_text_centered(image, self.buttons['left'], (button_l_x, button_l_y), button_font, self.theme.COLOR_PRIMARY)
        
        # draw the right button
        if self.buttons['right'] is not None:
            button_r_text_size = context.textsize(self.buttons['right'], button_font)
            # by default the button is centered
            button_r_x = self.xy[0] + dialog_margin + button_r_text_size[1]
            button_r_y = self.xy[1] + self.height / 2 + button_distance
                
            btnr_fill = self.theme.COLOR_SELECTION if self.selected_button == 'right' else self.theme.COLOR_BACKGROUND
            buttonr_selection = (button_center_x - selection_size[1] / 2,
                                button_r_y - selection_size[0] / 2, 
                                button_center_x + selection_size[1] / 2,
                                button_r_y + selection_size[0] / 2)
            context.rectangle(buttonr_selection, fill=btnr_fill, outline=self.theme.COLOR_PRIMARY)
                
            draw_rotated_text_centered(image, self.buttons['right'], (button_r_x, button_r_y), button_font, self.theme.COLOR_PRIMARY)