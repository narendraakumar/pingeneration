import os
import os.path
import random

import numpy as np

from models import Img, Text, ImageProcess, ImagesGroup
from utils import get_abs_path, pinproperties


class Pin:
    font_index = random.randint(0, 215)
    font_name = None
    draw_txt = False
    print(font_index)

    def __init__(self, imgs: list, folder_path: str, desired_height=300, product_header='none',matrix_dim=(4,2)):
        super().__init__()
        if not all([False for p in imgs if type(p) != Img]):
            imgs = self.make_Img_obj(imgs)
        self.imgs = imgs
        self.folder = folder_path
        self.total_imgs = len(imgs)
        self.desired_height = desired_height
        self.product_header = product_header
        self.matrix_dim = matrix_dim

    @staticmethod
    def make_Img_obj(imgs: list):
        return [p if type(p) == Img else Img(p) for p in imgs]

    def write_heading_to_pin(self, txt_img, top_margin=15, fontsize=40, font_index=1):
        txt_obj = Text(txt=self.product_header, font_path=None, font_size=fontsize,
                       max_width=txt_img.width, font_index=font_index)

        width = txt_obj.txt_width
        x = (txt_img.width - width) // 2
        loc = (abs(x), min(top_margin, pinproperties.MAX_NUM.value))
        txt_obj.draw_text(img=txt_img,color=pinproperties.FONT_COLOR_HEADER.value, loc=loc)
        pass

    @staticmethod
    def img_matrix(matrix_dim=(4, 3), allign=None, all_imgs=[]):
        img_in_hor = matrix_dim[0]
        img_in_ver = matrix_dim[1]
        imgs_list = [all_imgs[i:i + img_in_hor] for i in range(0, len(all_imgs), img_in_hor)]
        img_matrix = [ImagesGroup(imgs=im_group,font_index=Pin.font_index) for im_group in imgs_list]
        return img_matrix

    def make_collage(self):
        l_margin = pinproperties.L_MARGIN.value
        v_gap = pinproperties.V_GAP.value
        h_gap = pinproperties.H_GAP.value
        header_font_size = pinproperties.HEADER_FONT_SIZE.value
        t_margin = pinproperties.T_MARGIN.value

        ImageProcess.calculation_img_prop(self.imgs)

        img_grp = Pin.img_matrix(all_imgs=self.imgs,matrix_dim=self.matrix_dim)

        pin_width, pin_height = self.pin_size_calculation(img_grp, header_height=header_font_size * 3)

        pin_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', color=(255, 255, 255))
        txt_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', transparent=True)
        self.write_heading_to_pin(txt_img, fontsize=header_font_size, top_margin=int(header_font_size / 2.3),
                                  font_index=Pin.font_index)

        y_next = t_margin
        for grp in img_grp:
            x_next = l_margin
            for im in grp.img_grp:
                img = im.thumbnail_img
                pin_img.merge_imgs(img, pin_loc=(x_next, y_next))
                y_text = y_next+grp.max[1]+h_gap
                if Pin.draw_txt:
                    img.txt.draw_text(img=txt_img, color=pinproperties.FONT_COLOR.value,loc=(x_next, y_text))
                x_next = x_next + v_gap + img.width
            y_next += grp.max[1] + grp.max_grp_txt_height(grp.img_grp) + v_gap*2

        pin_img.obj = pin_img.obj.convert('RGBA')
        blend_image: Img = pin_img.blend_imgs(txt_img)
        blend_image.write_img()
        print(blend_image.height)
        return blend_image


    def pin_size_calculation(self, img_grp, header_height=30):
        img_heights = []
        pin_width = 0
        for grp in img_grp:
            grp: ImagesGroup
            max_txt_height = getattr(grp, 'max_txt_height', None)
            pin_width = max(pin_width, sum(grp.group_img_widths) + (len(grp) - 1) * pinproperties.V_GAP.value)
            img_heights.append(max(grp.group_img_heights) + max_txt_height + pinproperties.H_GAP.value * 2)
        pin_height = sum(img_heights) + header_height
        pin_width = pin_width + pinproperties.L_MARGIN.value + pinproperties.R_MARGIN.value
        return pin_width, pin_height


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
    pin = Pin(imgs=imgs_loaded, folder_path=imgs_folder, product_header='TOP FOUR PRODUCTS',matrix_dim=(4,2))
    res = pin.make_collage()
    res.show_img()
