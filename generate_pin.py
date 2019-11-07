import os
import os.path
import tempfile

import numpy as np
from PIL import Image

from models import Img, Text


class Pin:

    def __init__(self, imgs: list, folder_path: str, desired_height=300, product_header='none'):
        super().__init__()
        if not all([False for p in imgs if type(p) != Img]):
            imgs = self.make_Img_obj(imgs)
        self.imgs = imgs
        self.folder = folder_path
        self.total_imgs = len(imgs)
        self.desired_height = desired_height
        self.product_header = product_header

    @staticmethod
    def make_Img_obj(imgs: list):
        return [p if type(p) == Img else Img(p) for p in imgs]

    @staticmethod
    def make_blank_img(img_size: tuple = (1000, 3000),
                       color: tuple = (245, 245, 245),
                       transparent: bool = False, folder_path=None, write=False):
        if transparent:
            img_type = 'RGBA'
            color = (0, 0, 0, 0)
        else:
            img_type = 'RGB'

        img = Image.new(img_type, img_size, color)
        file_path = tempfile.NamedTemporaryFile(suffix='.jpg').name
        # if folder_path:
        #     file_path = folder_path + file_path
        pin_img = Img(file_path)
        pin_img.obj = img
        if not transparent and write:
            pin_img.write_img(file_path=file_path)
        return pin_img

    def aspect_ratio_equalizer(self):
        a_r = [im.aspect_ratio for im in self.imgs]
        median_ar = 1
        h_pad = 0
        if len(a_r) > 0:
            median_ar = float(np.median(a_r))
        for i, im in enumerate(self.imgs):
            if abs(im.aspect_ratio - median_ar) < 0.4:
                continue
            new_width = int((median_ar) * im.height)
            new_height = int(im.width / median_ar)

            if new_height > new_width:
                new_dim = (im.width, new_height)
            else:
                new_dim = (new_width, im.height)

            if len(self.imgs) - 1 == i:
                h_pad = int(((new_dim[0] - im.width) / 2) * (self.desired_height / im.height))
            im.padding(new_dim)
        return h_pad

    def make_collage(self):
        h_line = 1
        v_line = 1
        l_margin = 10
        r_margin = 10
        b_margin = 30
        v_gap = 20
        h_gap = 40
        font_size = 20
        header_font_size = font_size * 2
        t_margin = 10 + int(header_font_size * 3)
        img_height = self.desired_height
        total_v_gap = v_gap * v_line
        total_h_gap = h_gap * h_line
        pad_o = self.aspect_ratio_equalizer()
        l_margin = l_margin + pad_o
        imgs = self.make_imgs_equal_height(_height=img_height)
        h_pad = l_margin + r_margin + total_v_gap
        v_pad = t_margin + b_margin + total_h_gap
        tot_heights_imgs = len(imgs) * 300

        d = []
        for _img in self.imgs:
            print(_img.aspect_ratio)
            img = _img.thumbnail_img
            txt_obj = Text(txt=str(_img.name_without_ext), font_path=None, font_size=font_size, max_width=img.width)
            # txt_obj.get_all_fonts('/home/narendra/Documents/pinp/Font Pack.zip')
            d.append(txt_obj.get_text_height())
            setattr(img, 'txt', txt_obj)

        pin_height = v_pad + max(d) + img_height
        pin_width = sum(self.get_imgs_dim(imgs)[0]) + (len(imgs) - 1) * v_gap + l_margin + r_margin
        pin_img = Pin.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', color=(255, 255, 255))
        txt_img = Pin.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', transparent=True)

        self.write_heading_to_pin(txt_img, fontsize=header_font_size)

        x_next = l_margin
        y = t_margin + 300 + h_gap
        for img in imgs:
            pin_img.merge_imgs(img, pin_loc=(x_next, t_margin))
            img.txt.draw_text(img=txt_img, loc=(x_next, y))
            x_next = x_next + v_gap + img.width

        pin_img.obj = pin_img.obj.convert('RGBA')
        blend_image: Img = pin_img.blend_imgs(txt_img)
        blend_image.write_img()
        return blend_image

    def make_imgs_equal_height(self, _height=300):
        thumb_objs = []
        for img in self.imgs:
            thumbnail_img = img.resize(new_height=300)
            setattr(img, 'thumbnail_img', thumbnail_img)
            thumb_objs.append(thumbnail_img)
        return thumb_objs

    def get_imgs_dim(self, imgs_objs):
        all_widths = [ob.width for ob in imgs_objs]
        all_heights = [ob.height for ob in imgs_objs]
        return all_widths, all_heights

    def write_heading_to_pin(self, txt_img, top_margin=15, fontsize=40):
        txt_obj = Text(txt=self.product_header, font_path=None, font_size=fontsize, max_width=txt_img.width)
        width = txt_obj.txt_width
        x = (txt_img.width - width) // 2
        loc = (x, top_margin)
        txt_obj.draw_text(img=txt_img, loc=loc)
        pass


def read_img_files(file_path):
    imgs = []
    valid_images = [".jpg", ".gif", ".png", ".tga"]
    for f in os.listdir(file_path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        imgs.append(os.path.join(file_path, f))
    return imgs


# def get_size_of_pin(images):
#     for
#     pass


if __name__ == '__main__':
    imgs_loaded = read_img_files('/home/narendra/Documents/pinp')
    # draw_text("This could be a single line text but its too long to fit in one.")
    pin = Pin(imgs=imgs_loaded, folder_path='/home/narendra/Documents/pinp', product_header='TOP 5 PRODUCTS')
    res = pin.make_collage()
