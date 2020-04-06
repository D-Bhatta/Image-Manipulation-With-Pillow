import logging
import logging.config
from json import load as jload
from PIL import Image, ImageFilter,ImageDraw, ImageFont, ImageOps
# for batch processing
import os, glob

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
    def crop(self):
        self.load()
        im = self.im
        im_crop = im.crop((120,80,400,150))
        self.save_img_jpg("cropped_img", im_crop)
    def crop_center(self, im, crop_width, crop_height):
        img_width, img_height = im.size

        return im.crop((((img_width-crop_width)//2),
                        ((img_height-crop_height)//2),
                        ((img_width+crop_width)//2),
                        ((img_height+crop_height)//2))
                                                    )
    def center_crop(self):
        self.load()
        im = self.im
        im = self.crop_center(im, 150, 200)
        self.save_img_jpg("center_cropped", im)
    def max_square_crop(self):
        self.load()
        im = self.im
        im = self.crop_center(im, (min(im.size)), (min(im.size)))
        self.save_img_jpg("square_crop", im)
    def invert_image(self):
        """ Inverting an image with the invert function in the experimental ImageOps module """
        self.load()
        im = self.im
        # invert the image
        im_invert = ImageOps.invert(im)
        self.save_img_jpg("inverted", im_invert)
    def invert_rgba(self):
        """ Inverting a transparent png with mode RBGA """
        # convert to RGB from RGBA
        im = Image.open("src/horse.png")
        im = im.convert("RGB")
        im_invert = ImageOps.invert(im)
        self.save_img_jpg("inverted_rgba", im_invert)
    def crop_max_square(self,im):
        return self.crop_center(im, (min(im.size)), (min(im.size)))
    def expand_to_square(self,im,bgcolor):
        width, height = im.size
        if width == height:
            return im
        elif width > height:
            result = Image.new(im.mode, (width,width), bgcolor)
            result.paste(im, (0,(width-height)//2))
            return result
        else:
            result = Image.new(im.mode, (height, height), bgcolor)
            result.paste(im,((height-width)//2, 0))
            return result
    def mask_circle_solid(self,im,bgcolor,blur_radius,offset=0):
        background = Image.new(im.mode, im.size, bgcolor)

        offset = blur_radius*2 + offset
        mask = Image.new("L", im.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, im.size[0] - offset, im.size[1] - offset), fill = 255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        return Image.composite(im,background, mask)
    def mask_circle_transparent(self, im, blur_radius, offset=0):
        offset = blur_radius * 2 + offset
        mask = Image.new("L", im.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, im.size[0] - offset, im.size[1] - offset), fill = 255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = im.copy()
        result.putalpha(mask)
        return result
    def thumbnail(self):
        """ Generates TODO thumbnails using TODO methods"""
        self.load()
        im = self.im
        # crop into a rectangle
        thumb_width = 150
        # Rectangular square crop
        im_thumb = self.crop_center(im, thumb_width, thumb_width)
        self.save_img_jpg("rectangle_crop1", im_thumb)
        im_thumb = self.crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
        self.save_img_jpg("rectangle_crop2", im_thumb)
        # Adding margins to make a square
        im_thumb = self.expand_to_square(im,(0,0,0)).resize((thumb_width, thumb_width), Image.LANCZOS)
        self.save_img_jpg("margin_crop", im_thumb)
        # crop into a circle
        # solid bg
        im_square = self.crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
        im_thumb = self.mask_circle_solid(im_square, (0,0,0), 4)
        self.save_img_jpg("circle_bg_solid", im_thumb)
        # transparent bg
        im_square = self.crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
        im_thumb = self.mask_circle_transparent(im_square, 4)
        im_thumb.save("circle_bg_transparent.png")
    def batch_thumbnail(self):
        src_dir = 'data/src'
        dst_dir = 'data/dest'
        files = glob.glob(os.path.join(src_dir, '*.jpg'))

        for f in files:
            im = Image.open(f)
            im_thumb = self.crop_max_square(im).resize((150 ,150), Image.LANCZOS)
            ftitle, fext = os.path.splitext(os.path.basename(f))
            im_thumb.save(os.path.join(dst_dir, ftitle + "_thumbnail" + fext), quality=95)


pill = Pillow()
lg.info("printing image data...")
pill.print_data(pill.pillow_image_data())
lg.info("processing image...")
pill.process_image()
lg.info("Drawing a new image...")
pill.draw()
lg.info("Cropping the image custom, center, and max square...")
pill.crop()
pill.center_crop()
pill.max_square_crop()
lg.info("Inverting an RGB and an RGBA image")
pill.invert_image()
pill.invert_rgba()
pill.thumbnail()
pill.batch_thumbnail()