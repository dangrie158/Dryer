# utils.py
from PIL import Image, ImageDraw, ImageFont, ImageOps

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    context = image.draw()
    width, height = context.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    position = tuple(int(x) for x in position)
    image.buffer.paste(rotated, position, rotated)
    
def draw_rotated_text_centered(image, text, xy, font, color):
    context = image.draw()
    size = context.textsize(text, font)
    draw_rotated_text(image, text, (xy[0], xy[1] - size[0] / 2), -90, font, color)
    
def load_image(image_file, theme):
    image = Image.open(image_file).rotate(-90).convert('RGBA')
    return image

def paste_image(target, image, position, theme):
    if theme.INVERT_ICONS:
        inverted = ImageOps.invert(image.convert('RGB'))
        _, _, _, a = image.split()
        r, g, b = inverted.split()
        image =  Image.merge('RGBA', (r, g, b, a))
        
    target.buffer.paste(image, position, image)  