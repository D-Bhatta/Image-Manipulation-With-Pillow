import logging
import logging.config
from json import load as jload
from PIL import Image, ImageFilter,ImageDraw, ImageFont

# Configure logger lg with config for appLogger from config.json["logging"]
with open('config.json', 'r') as f:
    config = jload(f)
    logging.config.dictConfig(config["logging"])
lg = logging.getLogger('appLogger')
# lg.debug('Log starts here')


class Pillow(object):
    def __init__(self):
        self.im = Image.open('src/lenna_square.png')
    def load(self):
        self.im = Image.open('src/lenna_square.png')
    def pillow_image_data(self):
        im = self.im
        image_data = []
        image_data.append(("Size:(width, height): ",im.size))
        image_data.append(("Format: ", im.format))
        image_data.append(("Mode: ", im.mode))
        image_data.append(("Max and min values of RGB: ", im.getextrema()))
        image_data.append(("Pixel data at (0,0) : ",im.getpixel((0,0))))
        return image_data
    def print_data(self,image_data):
        for (text, value) in image_data:
            print(text, value)
    def process_image(self):
        """ Convert to grayscale, rotae by 90, and apply gaussian blur """
        im = self.im
        new_im = im.convert('L').rotate(90).filter(ImageFilter.GaussianBlur())
        self.save_img_jpg("processed_img1",new_im)
    def save_img_jpg(self,name,new_im):
        name = name + ".jpg"
        new_im.save(name,quality=95)
    def draw(self):
        im = Image.new("RGB", (512,512), (128,128,128))
        draw = ImageDraw.Draw(im)
        draw.line((0, im.height,im.width, 0), fill=(255,0,0), width=0)
        draw.rectangle((100,100,200,200), fill=(0,255,0))
        draw.ellipse((250,300,450,400), fill=(0,0,255))
        font = ImageFont.truetype('FreeMono.ttf', 48)
        draw.multiline_text((0,0), 'Pillow Sample', fill=(0,0,0), font=font)
        
        self.save_img_jpg("pillow_drawing1", im)
    




pill = Pillow()
lg.info(pill.pillow_image_data())
pill.print_data(pill.pillow_image_data())
pill.process_image()
pill.draw()


