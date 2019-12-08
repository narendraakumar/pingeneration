import os
import os.path
import random
from copy import deepcopy

import numpy as np

from image_prosess import alpha_composite
from models import Img, Text, ImageProcess, ImagesGroup, TextList
from utils import get_abs_path, pinproperties




class Pin:
    # font_index = random.randint(0, 215)
    font_name = None
    draw_txt = False

    def __init__(self, imgs: list, folder_path: str, desired_height=300,
                 product_header=[], matrix_dim=(4, 2), font_index=1, text_list=[]):
        super().__init__()
        if not all([False for p in imgs if type(p) != Img]):
            imgs = self.make_Img_obj(imgs)
        setattr(Pin, 'font_index', font_index)
        self.imgs = imgs
        self.folder = folder_path
        self.total_imgs = len(imgs)
        self.desired_height = desired_height
        self.product_header = product_header
        self.matrix_dim = matrix_dim
        self.max_width = pinproperties.MAX_WIDTH_FOR_TXT.value
        self.txt_list = text_list
        setattr(Pin, 'max_width', self.max_width)

    @staticmethod
    def make_Img_obj(imgs: list):
        return [p if type(p) == Img else Img(p) for p in imgs]

    def write_txt_on_img(self, txt_img, txt = [], top_margin=15, fontsize=40, font_index=1,font_color=None,max_width=0):
        txt_objs = []
        for p_h in txt:
            txt_objs.append(Text(txt=p_h, font_path=None, font_size=fontsize,
                                 max_width=txt_img.width, font_index=font_index))
        y = min(top_margin, pinproperties.MAX_NUM.value)
        header_txt_h = 0
        if font_color is None:
            font_color = pinproperties.FONT_COLOR_HEADER.value
        for txt_obj in txt_objs:
            width = txt_obj.txt_width
            x = (txt_img.width - width) // 2
            loc = (abs(x), y)
            txt_obj.draw_text(img=txt_img, color=font_color, loc=loc,max_width=max_width)
            y += txt_obj.max_height
            header_txt_h += txt_obj.max_height
        return header_txt_h

    def write_txt_on_img_v(self, txt_img, top_margin=15, max_width=0, txt_config=None):

        font_size_list = txt_config.get('font_size', [])
        font_idx_list = txt_config.get('font_idx', [])
        font_clr = txt_config.get('font_clr', [])
        txt = txt_config.get('txt',[])
        txt_objs = []
        for i, txt in enumerate(txt):
            fnt_sz = font_size_list[i] if i < len(font_size_list) else 60
            fnt_idx = font_idx_list[i] if i < len(font_idx_list) else 45
            clr = font_clr[i] if i < len(font_clr) else 'rgb(255, 255 ,255)'
            txt_objs.append(Text(txt=txt, font_path=None, font_size=fnt_sz,
                                 max_width=txt_img.width, font_index=fnt_idx,font_color=clr))

        y = min(top_margin, pinproperties.MAX_NUM.value)
        header_txt_h = 0

        for txt_obj in txt_objs:
            width = txt_obj.txt_width
            x = (txt_img.width - width) // 2
            loc = (abs(x), y)
            txt_obj.draw_text(img=txt_img, color=txt_obj.font_color, loc=loc, max_width=max_width)
            y += txt_obj.max_height
            header_txt_h += txt_obj.max_height
        return header_txt_h

    @staticmethod
    def img_matrix(matrix_dim=(4, 3), allign=None, all_imgs=[]):
        img_in_hor = matrix_dim[0]
        img_in_ver = matrix_dim[1]
        imgs_list = [all_imgs[i:i + img_in_hor] for i in range(0, len(all_imgs), img_in_hor)]
        img_matrix = [ImagesGroup(imgs=im_group, font_index=Pin.font_index, max_width=Pin.max_width) for im_group in
                      imgs_list]
        return img_matrix

    def make_collage(self):

        header_font_size = pinproperties.HEADER_FONT_SIZE.value
        t_margin = int(header_font_size / 2.3)
        pinproperties.T_MARGIN._value_ = t_margin
        ImageProcess.calculation_img_prop(self.imgs)

        img_grp = Pin.img_matrix(all_imgs=self.imgs, matrix_dim=self.matrix_dim)

        pin_width, pin_height = self.pin_size_calculation(img_grp, header_font_size=header_font_size)

        pin_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', color=(255, 255, 0))
        txt_img = Img.make_blank_img(img_size=(pin_width, pin_height), folder_path='/tmp/', transparent=True)
        header_max_height = self.write_txt_on_img(txt_img,txt = self.product_header, fontsize=header_font_size,
                                                  top_margin=t_margin,
                                                  font_index=Pin.font_index,max_width=txt_img.width)

        txt_img, pin_img = self.img_merging(txt_img, pin_img, img_grp, t_margin)
        pin_img.obj = pin_img.obj.convert('RGBA')
        blend_image: Img = pin_img.blend_imgs(txt_img)
        txt_config = {'font_size':[40,50,60,70]*2,'font_idx':[10]*8,'font_clr':['rgb(255, 255 ,255)']*8,'txt':self.txt_list*2}
        top_layer = self.make_top_layer(size=(pin_width,pin_height),txt_config=txt_config)
        blend_image.obj = alpha_composite(top_layer.obj,blend_image.obj)
        blend_image.write_img()
        return blend_image

    def img_merging(self, txt_img, pin_img, img_grp, t_margin):
        l_margin = pinproperties.L_MARGIN.value
        v_gap = pinproperties.V_GAP.value
        h_gap = pinproperties.H_GAP.value
        x_next = l_margin

        start_p = getattr(self, "start_p")
        if pinproperties.V_ALLIGN.value:
            for grp in img_grp:
                y_next = start_p
                for im in grp.img_grp:
                    img = im.thumbnail_img
                    pin_img.merge_imgs(img, pin_loc=(x_next, y_next))
                    x_text = x_next + img.width + v_gap
                    if pinproperties.WRITE_TXT.value:
                        img.txt.draw_text(img=txt_img, color=pinproperties.FONT_COLOR.value,
                                          loc=(x_text, y_next + t_margin),max_width=self.max_width)
                    y_next = y_next + h_gap + img.height
                x_next += grp.max[0] + grp.max_grp_txt_width(grp.img_grp) + v_gap * 2
        else:
            y_next = start_p
            for grp in img_grp:
                x_next = l_margin
                for im in grp.img_grp:
                    img = im.thumbnail_img
                    pin_img.merge_imgs(img, pin_loc=(x_next, y_next))
                    y_text = y_next + grp.max[1] + h_gap
                    if pinproperties.WRITE_TXT.value:
                        img.txt.draw_text(img=txt_img, color=pinproperties.FONT_COLOR.value, loc=(x_next, y_text),max_width=img.width)
                    x_next = x_next + v_gap + img.width
                y_next += grp.max[1] + grp.max_grp_txt_height(grp.img_grp) + v_gap * 2
        return txt_img, pin_img

    def pin_size_calculation(self, img_grp, header_font_size=40, max_width=2000):
        img_heights = []
        img_widths = []
        pin_height = 0
        pin_width = 0
        if pinproperties.V_ALLIGN.value:
            for grp in img_grp:
                grp: ImagesGroup
                pin_height = max(pin_height, sum(grp.group_img_heights) + (len(grp)) * pinproperties.H_GAP.value)
                img_widths.append(max(grp.group_img_widths) + self.max_width + pinproperties.V_GAP.value * self.matrix_dim[1])

            pin_width = sum(img_widths) + pinproperties.L_MARGIN.value + pinproperties.R_MARGIN.value

            header = TextList(t_list=self.product_header, font_size=header_font_size, max_width=pin_width)
            start_p = header.get_max_txt_height() + pinproperties.T_MARGIN.value
            setattr(self, "start_p", start_p)
            pin_height += header.get_max_txt_height() + pinproperties.B_MARGIN.value

        else:
            for grp in img_grp:
                grp: ImagesGroup
                max_txt_height = getattr(grp, 'max_txt_height', None)
                pin_width = max(pin_width, sum(grp.group_img_widths) + (len(grp) - 1) * pinproperties.V_GAP.value)
                img_heights.append(max(grp.group_img_heights) + max_txt_height + pinproperties.H_GAP.value * self.matrix_dim[0])

            pin_width = pin_width + pinproperties.L_MARGIN.value + pinproperties.R_MARGIN.value
            header = TextList(t_list=self.product_header, font_size=header_font_size, max_width=pin_width)
            start_p = header.get_max_txt_height() + pinproperties.T_MARGIN.value
            setattr(self, "start_p", start_p)
            pin_height = sum(img_heights) + start_p + pinproperties.B_MARGIN.value

        return pin_width, pin_height

    def make_top_layer(self,size: tuple, text: list = [],txt_config=None):
        layer_img_1 = Img.make_blank_img(img_size=(size), folder_path='/tmp/', color=(0, 0, 0, 0), transparent=True)
        layer_img_2 = deepcopy(layer_img_1)
        layer_img_3 = Img.make_blank_img(img_size=(size[0]-50, 350), folder_path='/tmp/', color=(153, 0, 153, 150),
                                         transparent=True)
        if txt_config is not None:
            self.write_txt_on_img_v(txt_img=layer_img_3, top_margin=10, max_width=layer_img_3.width, txt_config=txt_config)
        else:
            self.write_txt_on_img(txt_img=layer_img_3,txt=self.txt_list, top_margin=10, fontsize=60, font_index=45,font_color='rgb(255, 255 ,255)',max_width=layer_img_3.width)

        layer_img_2.merge_imgs(layer_img_3, pin_loc=(
        int(layer_img_2.width / 2 - layer_img_3.width / 2), int(layer_img_2.height / 2 - layer_img_3.height / 2)))
        return layer_img_2


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
    matrix_dim = (4,2)
    imgs_loaded = imgs_loaded[:matrix_dim[0] * matrix_dim[1]]
    # all_fonts = Text(zip_file_path=get_abs_path('/Font Pack.zip'),font_index=1)
    # Text.write_fonts_on_image(all_fonts)
    # imags_folder where all intermediate files get saved
    text_list=['TOP FOUR PRODUCTS', 'CHECK THEM', 'TOP FOUR PRODUCTS']
    product_header=['IF YOU WANT EAT SOMETHING SPECIAL', ' LEST CHECK SOME COOL PINS']
    pin = Pin(imgs=imgs_loaded, folder_path=imgs_folder,
              product_header=[],
              matrix_dim=matrix_dim, font_index=20,text_list=text_list)
    res = pin.make_collage()
    res.show_img()
    # res.write_img(file_path='/home/narendra/imgs/'+str(10)+".jpg")
