import logging
import logging.config
from json import load as jload
from PIL import Image, ImageFilter,ImageDraw, ImageFont, ImageOps
# for batch processing
import os, glob
import qrcode

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
    def concatenate(self):
        self.load()
        im1 = self.im
        im2 = self.im
        concatenated_img = self.get_concat_h(im1,im2)
        self.save_img_jpg('concatenated_same_height', concatenated_img)
        concatenated_img = self.get_concat_v(im1,im2)
        self.save_img_jpg('concatenated_same_width', concatenated_img)
        im2 = Image.open('src/rocket.jpg')
        concatenated_img = self.get_concat_h_cut(im1,im2)
        self.save_img_jpg('concatenated_cut', concatenated_img)
        concatenated_img = self.get_concat_v_cut(im1,im2)
        self.save_img_jpg('concatenated_cut', concatenated_img)
        concatenated_img = self.get_concat_h_cut_center(im1,im2)
        self.save_img_jpg('concatenated_cut_center', concatenated_img)
        concatenated_img = self.get_concat_v_cut_center(im1,im2)
        self.save_img_jpg('concatenated_cut_center', concatenated_img)
        concatenated_img = self.get_concat_h_blank(im1,im2,(0,0,0))
        self.save_img_jpg('concatenated_blank', concatenated_img)
        concatenated_img = self.get_concat_v_blank(im1,im2,(0,50,200))
        self.save_img_jpg('concatenated_blank', concatenated_img)
        concatenated_img = self.get_concat_h_resize(im1,im2)
        self.save_img_jpg('concatenated_height_resize', concatenated_img)
        concatenated_img = self.get_concat_v_resize(im1,im2,resize_big_image=False)
        self.save_img_jpg('concatenated_width_resize', concatenated_img)
        concatenated_img = self.concat_multiple([im1,im2,im1])
        self.save_img_jpg('concatenated_multiple', concatenated_img)
        im_s = im1.resize((im1.width // 2, im1.height // 2))
        concatenated_img = self.get_concat_tile_repeat(im_s,3,4)
        self.save_img_jpg('concatenated_tile', concatenated_img)
    def get_concat_h(self,im1,im2):
        dest = Image.new('RGB', (im1.width + im2.width, im1.height))
        dest.paste(im1,(0,0))
        dest.paste(im2, (im1.width,0))
        return dest
    def get_concat_v(self,im1,im2):
        dest = Image.new('RGB', (im1.width, im1.height + im2.height))
        dest.paste(im1,(0, 0))
        dest.paste(im2, (0, im1.height))
        return dest
    def get_concat_h_cut(self,im1,im2):
        dest =  Image.new('RGB', (im1.width+im2.width, min(im1.height, im2.height)))
        dest.paste(im1,(0,0))
        dest.paste(im2,(im1.width,0))
        return dest
    def get_concat_v_cut(self,im1, im2):
        dest = Image.new('RGB', (min(im1.width,im2.width),im1.height+im2.height))
        dest.paste(im1,(0,0))
        dest.paste(im2,(0,im1.height))
        return dest
    def get_concat_h_cut_center(self,im1,im2):
        dest =  Image.new('RGB', (im1.width+im2.width, min(im1.height, im2.height)))
        dest.paste(im1,(0,0))
        dest.paste(im2,(im1.width,((im1.height-im2.height)//2)))
        return dest
    def get_concat_v_cut_center(self,im1, im2):
        dest = Image.new('RGB', (min(im1.width,im2.width),im1.height+im2.height))
        dest.paste(im1,(0,0))
        dest.paste(im2,(((im1.width-im2.width)//2),im1.height))
        return dest
    def get_concat_h_blank(self,im1,im2,color=(0,0,0)):
        dest = Image.new('RGB', (im1.width+im2.width, max(im1.height, im2.height)), color=color)
        dest.paste(im1,(0,0))
        dest.paste(im2,(im1.width,0))
        return dest
    def get_concat_v_blank(self, im1, im2, color=(0,0,0)):
        dest = Image.new('RGB', (max(im1.width,im2.width), im1.height+im2.height), color=color)
        dest.paste(im1,(0,0))
        dest.paste(im2,(0,im1.height))
        return dest
    def get_concat_h_resize(self,im1,im2, resample=Image.BICUBIC, resize_big_image=True):
        if im1.height == im2.height:
            _im1 = im1
            _im2 = im2
        elif (((im1.height > im2.height) and resize_big_image)or ((im1.height < im2.height)and not resize_big_image)):
            _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
            _im2 = im2
        else:
            _im1 = im1
            _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
        dest = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
        dest.paste(_im1, (0,0))
        dest.paste(_im2,(_im1.width, 0))
        return dest
    def get_concat_v_resize(self,im1,im2, resample=Image.BICUBIC, resize_big_image=True):
        if im1.width == im2.width:
            _im1 = im1
            _im2 = im2
        elif (((im1.width > im2.width) and resize_big_image)or ((im1.width < im2.width)and not resize_big_image)):
            _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
            _im2 = im2
        else:
            _im1 = im1
            _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)
        dest = Image.new('RGB', (_im1.width, _im2.height+ _im1.height))
        dest.paste(_im1, (0,0))
        dest.paste(_im2,(0,_im1.height))
        return dest
    def concat_multiple(self,im_list):
        _im = im_list.pop(0)
        for im in im_list:
            _im = self.get_concat_h(_im,im)
        return _im
    def get_concat_h_repeat(self,im,column):
        dest = Image.new('RGB', (im.width*column, im.height))
        for x in range(column):
            dest.paste(im,(x*im.width,0))
        return dest
    def get_concat_v_repeat(self, im, row):
        dest = Image.new('RGB', (im.width,im.height*row))
        for y in range(row):
            dest.paste(im, (0,y*im.height))
        return dest
    def get_concat_tile_repeat(self,im, row, column):
        dest_h = self.get_concat_h_repeat(im, column)
        return self.get_concat_v_repeat(dest_h, row)
    def gen_qr_code(self):
        """ generates a qr code of a link(https://www.bhg.com.au/colours-that-go-with-blue-complementary-colours-for-blue) and embeds it into an image. 

        the qr code has a high error correction, a blue background(#002366) and gray foreground(#C0C0C0).

        the qr code is embedded on the blue couch image.
        """
        img_bg = Image.open('src/blue-couch.jpg')
        data = "https://www.bhg.com.au/colours-that-go-with-blue-complementary-colours-for-blue"
        fg = "#002366"
        bg = '#C0C0C0'
        im = self.gen_qr_util(img_bg,data,fg,bg)
        self.save_img_jpg('qr_code_embedded', im)
        
    def gen_qr_util(self, im, data, fg, bg):
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=2,
            border=2
        )
        qr.add_data(str(data))
        qr.make()
        img = qr.make_image(fill_color=bg, back_color=fg)
        pos = (im.size[0] - img.size[0],im.size[1] - img.size[1])
        im.paste(img,pos)
        return im

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
pill.concatenate()
lg.info('Embedding a qr code into an image...')
pill.gen_qr_code()