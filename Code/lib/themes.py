# themes.py
from PIL import ImageFont

class LightTheme:
    COLOR_HUMIDITY = (0x47, 0x86, 0xBA)
    COLOR_TEMPERATURE = (0xD3, 0x9E, 0x29)
    COLOR_SELECTION = (0xD3, 0x9E, 0x29)
    COLOR_EDIT = (0x47, 0x86, 0xBA)
    COLOR_PRIMARY = (0x00, 0x00, 0x00)
    COLOR_BACKGROUND = (0xFF, 0xFF, 0xFF)
    
    FONT_LEGEND = ImageFont.truetype('resources/fonts/SourceCodePro-Regular.ttf', size=10)
    FONT_REGULAR = ImageFont.truetype('resources/fonts/SourceCodePro-Regular.ttf', size=15)
    FONT_REGULAR_BOLD = ImageFont.truetype('resources/fonts/SourceCodePro-Bold.ttf', size=15)
    FONT_SMALL = ImageFont.truetype('resources/fonts/SourceCodePro-Regular.ttf', size=11)
    FONT_BIG = ImageFont.truetype('resources/fonts/SourceCodePro-Bold.ttf', size=20)
    
    INVERT_ICONS = False
    
class DarkTheme(LightTheme):
    COLOR_HUMIDITY = (0x3D, 0x7A, 0xC7)
    COLOR_TEMPERATURE = (0xBD, 0x35, 0x12)
    COLOR_SELECTION = (0xBD, 0x35, 0x12)
    COLOR_EDIT = (0x3D, 0x7A, 0xC7)
    COLOR_PRIMARY = (0xCC, 0xC6, 0xCA)
    COLOR_BACKGROUND = (0x1F, 0x1F, 0x20)
    
    INVERT_ICONS = True