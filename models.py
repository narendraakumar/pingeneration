import glob
import os
import tempfile
import zipfile
from collections import OrderedDict
from copy import deepcopy

import numpy as np
from PIL import Image, ImageFont, ImageDraw

from utils import get_abs_path, write_to_file, read_from_file


class Img:
    obj = None

    def __init__(self, file_path):
        self.file_path = file_path
        self.folder_path, self.name_without_ext, self.ext, \
        self.file_name_without_ext = Img.splitext(self.file_path)
        self.child_obj = []
        self.resize_obj = None

    def load(self):
        try:
            self.obj = Image.open(os.path.join(self.file_path))
        except Exception as e:
            print(str(e))

    @property
    def height(self):
        if self.obj is not None:
            return self.obj.size[1]
        else:
            self.load()
            return self.obj.size[1]

    @property
    def width(self):
        if self.obj is not None:
            return self.obj.size[0]
        else:
            self.load()
            return self.obj.size[0]

    @property
    def size(self):
        return self.height * self.width

    @property
    def aspect_ratio(self):
        return self.width / self.height

    def unload(self):
        if self.obj is not None:
            self.obj = None

    @staticmethod
    def splitext(path):
        file_name_without_ext, ext = os.path.splitext(path)
        folder_path, name_without_ext = os.path.split(file_name_without_ext)
        return folder_path, name_without_ext, ext, file_name_without_ext

    def write_img(self, file_path=None, overwrite=True, ext=None):
        if ext is None:
            ext = '.png'
        if self.obj.mode == 'RGBA':
            if self.obj == None:
                self.load()
            img_obj = self.obj.convert('RGB')
        else:
            img_obj = self.obj
        if img_obj is not None:
            if file_path is not None:
                img_obj.save(file_path, optimize=True)
                self.child_obj.append(Img(file_path))

            elif file_path is None and overwrite:
                img_obj.save(self.file_path, optmize=True)
            else:
                temp = tempfile.NamedTemporaryFile(suffix=ext)
                img_obj.save(temp.name, optimize=True)
                self.child_obj.append(Img(temp.name))
            return True
        else:
            raise str('writable obj not available')

    def show_img(self):
        if self.obj is None:
            self.load()
        self.obj.show()
        return True

    def resize(self, new_width=None, new_height=None, x_p=None, y_p=None, xy_p=None, unload=False):

        if self.obj is None:
            self.load()
        if new_width and new_height is None and x_p and y_p is not None and xy_p is None:
            new_width = int(x_p * self.width)
            new_height = int(y_p * self.height)
        elif xy_p is not None:
            new_width = int(xy_p * self.width)
            new_height = int(xy_p * self.height)
        elif new_height or new_width and not x_p and not y_p and not xy_p:
            if not new_width:
                new_width = int(new_height * self.width / self.height)
            elif not new_height:
                new_height = int(new_width * self.height / self.width)
        else:
            new_height = self.height
            new_width = self.width

        img = deepcopy(self.obj).resize((new_width, new_height), Image.ANTIALIAS)
        if not os.path.exists(self.folder_path + '/thumbnail'):
            os.mkdir(self.folder_path + '/thumbnail')
        resize_img = Img(file_path='/thumbnail/' + self.file_name_without_ext + '_thumbnail.jpg')
        resize_img.obj = img
        resize_img.write_img(file_path=self.folder_path + '/thumbnail/' + self.name_without_ext + '.jpg')
        if unload:
            resize_img.obj = None
        return resize_img

    def center(self):
        return int(self.width), int(self.height)

    def merge_imgs(self, foreground, pin_loc=(0, 0)):
        self.obj.paste(foreground.obj, pin_loc)
        return True

    def blend_imgs(self, bg_img, alpha=1.0, box=(0, 0)):
        fg_img_trans = Image.blend(self.obj, bg_img.obj, alpha)
        bg_img.obj.paste(fg_img_trans, box, fg_img_trans)
        bg_img.obj = Image.alpha_composite(self.obj, bg_img.obj)
        return bg_img

    def padding(self, dim, pad_color=(255, 255, 255)):

        # self.resize()
        new_im = Image.new("RGB", dim, color=pad_color)
        offset = ((new_im.size[0] - self.width) // 2, (new_im.size[1] - self.height) // 2)
        new_im.paste(self.obj, offset)
        self.obj = new_im
        return True

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


class Fonts:

    def __init__(self, zip_file_path=None):
        self.font_name_list = None
        if zip_file_path is None:
            zip_file_path = get_abs_path('/Font Pack.zip')
        self.zip_path = zip_file_path
        self.fonts = self.make_all_fonts(self.zip_path)

    def write_fonts_on_image(self):
        # all_fonts = read_from_file(file_path=get_abs_path('/fonts/fonts.txt'))
        all_fonts = self.fonts
        font_size = 20
        pin_width = 1500
        text_in_one_column = 70
        x = 20
        y = 20
        pin_height = int(20 * len(all_fonts) / 2.5)
        img = Img.make_blank_img(img_size=(pin_width, pin_height + 10), folder_path='/tmp/', color=(255, 255, 255))

        arr = np.arange(0, len(all_fonts), text_in_one_column)
        x_w = int(pin_width / len(arr))

        r = 1
        for i, font in enumerate(all_fonts):
            txt_obj = Text(txt=str('{}.  {}'.format(i, font)), font_path=all_fonts[font], font_size=font_size,
                           max_width=pin_width)
            y += (font_size + 8)
            if i / text_in_one_column >= r:
                r += 1
                x += x_w
                y = 20
            txt_obj.draw_text(img=img, loc=(x, y))
        img.write_img(file_path=get_abs_path('/fonts/fonts.jpg'))
        return True

    def choose_font(self, index: int = None, name: str = None):
        fonts = self.font_name_list
        if self.font_name_list is None:
            fonts = read_from_file(get_abs_path('/fonts/font.txt'))

        all_fonts = self.fonts
        if index is not None and len(all_fonts) > 0:
            return all_fonts[fonts[index]]
        elif name is not None and len(all_fonts) > 0:
            return all_fonts[fonts[index]]
        elif not name and not index:
            return get_abs_path('/pacifico/Pacifico.ttf')
        else:
            raise Exception('fonts are missing')

    def make_all_fonts(self, zip_file_path):

        dir = get_abs_path('/fonts')
        if not os.path.exists(dir):
            os.mkdir(dir)
        dirContents = os.listdir(dir)
        if len(dirContents) == 0:
            if not os.path.exists(dir):
                os.mkdir(dir)
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(dir)

        mylist = [f for f in glob.glob(dir + "/**/*.ttf", recursive=True)]
        # rmtree(tmp, ignore_errors=True)
        font_dict = OrderedDict((k.split('.')[0].split('/')[-1], k) for k in mylist)
        f_path = get_abs_path("/fonts/font.txt")
        setattr(self, 'font_name_list', list(font_dict.keys()))
        assert write_to_file(f_path, list(font_dict.keys()))
        return font_dict


class Text(Fonts):

    def __init__(self, txt: str = '', font_path=None, font_size=20, max_width=100,
                 zip_file_path=None, font_name=None, font_index=None):
        super().__init__(zip_file_path)
        self.txt = txt
        self.font_path = font_path
        self.max_width = max_width
        if font_path is None:
            font_path = self.choose_font(name=font_name, index=font_index)

        self.font = ImageFont.truetype(font_path, size=font_size, encoding="unic")

    @property
    def lower_case(self):
        self.txt = self.txt.lower()
        return True

    @property
    def upper_case(self):
        self.txt = self.txt.upper()
        return True

    @property
    def txt_width(self):
        return self.font.getsize(self.txt)[0]

    @property
    def txt_height(self):
        if self.font.getsize(self.txt)[0] <= self.max_width:
            return self.font.size
        else:
            return len(self.text_wrap()) * self.font.size

    def text_wrap(self):
        lines = []
        if self.font.getsize(self.txt)[0] <= self.max_width:
            lines.append(self.txt)
        else:
            # split the line by spaces to get words
            words = self.txt.split(' ')
            i = 0
            # append every word to a line while its width is shorter than image width
            while i < len(words):
                line = ''
                while i < len(words) and self.font.getsize(line + words[i])[0] <= self.max_width:
                    line = line + words[i] + " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1
                lines.append(line)
        return lines

    def get_text_height(self):
        return len(self.text_wrap()) * self.font.getsize('hg')[1]

    def draw_text(self, img, color='rgb(0, 0, 0)', loc: tuple = (10, 20)):
        if img.obj == None:
            img.load()
        line_height = self.font.getsize('hg')[1]
        draw = ImageDraw.Draw(img.obj)
        y = loc[1]
        for line in self.text_wrap():
            draw.text(loc, line, fill=color, font=self.font)
            y = y + line_height
            loc = (loc[0], y)
        return img


class Imgs:

    @staticmethod
    def make_imgs_equal_height(Pin, _height=300):
        thumb_objs = []
        for img in Pin.imgs:
            thumbnail_img = img.resize(new_height=300)
            setattr(img, 'thumbnail_img', thumbnail_img)
            thumb_objs.append(thumbnail_img)
        return thumb_objs

    @staticmethod
    def get_imgs_dim(imgs_objs):
        all_widths = [ob.width for ob in imgs_objs]
        all_heights = [ob.height for ob in imgs_objs]
        return all_widths, all_heights
