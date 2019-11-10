import os
import os.path
import random

import numpy as np

from models import Img, Text, Imgs, ImagesGroup
from utils import get_abs_path, pinproperties



class Pin:
    font_index = random.randint(0, 215)
    font_name = None

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

    def write_heading_to_pin(self, txt_img, top_margin=15, fontsize=40, font_index=1):
        txt_obj = Text(txt=self.product_header, font_path=None, font_size=fontsize,
                       max_width=txt_img.width, font_index=font_index)

        width = txt_obj.txt_width
        x = (txt_img.width - width) // 2
        loc = (abs(x), min(top_margin, pinproperties.MAX_NUM.value))
        txt_obj.draw_text(img=txt_img, loc=loc)
        pass

    def add_txt_obj(self, font_size):
        d = []
        # ims = Imgs.img_matrix(matrix_dim=(4,3),all_imgs=self.imgs)
        for _img in self.imgs:
            print(_img.aspect_ratio)
            img = _img.thumbnail_img
            txt_obj = Text(txt=str(_img.name_without_ext), font_path=None, font_size=font_size,
                           max_width=img.width, font_index=Pin.font_index)
            d.append(txt_obj.get_text_height())
            setattr(img, 'txt', txt_obj)
        setattr(self, 'max_txt_height', max(d))
        return True

    @staticmethod
    def img_matrix(matrix_dim=(4, 3), allign=None, all_imgs=[]):
        img_in_hor = matrix_dim[0]
        img_in_ver = matrix_dim[1]
        imgs_list = [all_imgs[i:i + img_in_hor] for i in range(0, len(all_imgs), img_in_hor)]
        img_matrix = [ImagesGroup(imgs=im_group) for im_group in imgs_list]
        return img_matrix

    def make_collage(self):
        h_line = pinproperties.H_LINE.value
        v_line = pinproperties.V_LINE.value
        l_margin = pinproperties.L_MARGIN.value
        r_margin = pinproperties.R_MARGIN.value
        b_margin = pinproperties.B_MARGIN.value
        v_gap = pinproperties.V_GAP.value
        h_gap = pinproperties.H_GAP.value
        font_size = pinproperties.FONT_SIZE.value
        header_font_size = font_size * 2

        t_margin = 10 + int(header_font_size * 3)
        img_height = self.desired_height

        total_v_gap = v_gap * v_line
        total_h_gap = h_gap * h_line

        pad_o = Imgs.aspect_ratio_equalizer(self)
        self.add_txt_obj(font_size)
        imgs = Imgs.make_imgs_equal_height(self, _height=img_height)

        l_margin = l_margin + pad_o
        h_pad = l_margin + r_margin + total_v_gap
        v_pad = t_margin + b_margin + total_h_gap

        img_grp = pin.img_matrix(all_imgs=self.imgs)

        max_txt_height = getattr(self,'max_txt_height',None)
        pin_height = v_pad + max_txt_height + img_height
        pin_width = sum(Imgs.get_imgs_dim(imgs)[0]) + (len(imgs) - 1) * v_gap + l_margin + r_margin
        pin_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', color=(255, 255, 255))
        txt_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', transparent=True)

        self.write_heading_to_pin(txt_img, fontsize=header_font_size, font_index=Pin.font_index)

        x_next = l_margin
        y = t_margin + self.desired_height + h_gap
        for img in imgs:
            pin_img.merge_imgs(img, pin_loc=(x_next, t_margin))
            img.txt.draw_text(img=txt_img, loc=(x_next, y))
            x_next = x_next + v_gap + img.width

        pin_img.obj = pin_img.obj.convert('RGBA')
        blend_image: Img = pin_img.blend_imgs(txt_img)
        blend_image.write_img()
        print(blend_image.height)
        return blend_image



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
    # imags_folder where all intermediate files get saved
    pin = Pin(imgs=imgs_loaded, folder_path=imgs_folder, product_header='TOP FOUR PRODUCTS')
    res = pin.make_collage()
    res.show_img()
