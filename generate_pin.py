import os
import os.path
import tempfile

import numpy as np
from PIL import Image

from models import Img, Text, Imgs
from utils import get_abs_path


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
        imgs = Imgs.make_imgs_equal_height(self,_height=img_height)
        h_pad = l_margin + r_margin + total_v_gap
        v_pad = t_margin + b_margin + total_h_gap
        tot_heights_imgs = len(imgs) * 300

        d = []
        for _img in self.imgs:
            print(_img.aspect_ratio)
            img = _img.thumbnail_img
            txt_obj = Text(txt=str(_img.name_without_ext), font_path=None, font_size=font_size, max_width=img.width,font_index=3)
            d.append(txt_obj.get_text_height())
            setattr(img, 'txt', txt_obj)

        pin_height = v_pad + max(d) + img_height
        pin_width = sum(Imgs.get_imgs_dim(imgs)[0]) + (len(imgs) - 1) * v_gap + l_margin + r_margin
        pin_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', color=(255, 255, 255))
        txt_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', transparent=True)

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


if __name__ == '__main__':
    imgs_folder = get_abs_path('/pics')
    imgs_loaded = read_img_files(imgs_folder)
    # all_fonts = Text(zip_file_path=get_abs_path('/Font Pack.zip'),font_index=1)
    # Text.write_fonts_on_image(all_fonts)
    pin = Pin(imgs=imgs_loaded, folder_path=imgs_folder, product_header='TOP FIVE PRODUCTS')
    res = pin.make_collage()
