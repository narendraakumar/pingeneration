from copy import deepcopy

from models import Img

import numpy as np
from PIL import Image, ImageDraw


def alpha_composite(src, dst):
    '''
    Return the alpha composite of src and dst.

    Parameters:
    src -- PIL RGBA Image object
    dst -- PIL RGBA Image object

    The algorithm comes from http://en.wikipedia.org/wiki/Alpha_compositing
    '''
    if src.mode == 'RGB':
        src.convert('RGBA')
    if dst.mode == 'RGB':
        dst.convert('RGBA')
    src = np.asarray(src)
    dst = np.asarray(dst)
    out = np.empty(src.shape, dtype='float')
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    src_a = src[alpha] / 255.0
    dst_a = dst[alpha] / 255.0
    out[alpha] = src_a + dst_a * (1 - src_a)
    old_setting = np.seterr(invalid='ignore')
    out[rgb] = (src[rgb] * src_a + dst[rgb] * dst_a * (1 - src_a)) / out[alpha]
    np.seterr(**old_setting)
    out[alpha] *= 255
    np.clip(out, 0, 255)
    # astype('uint8') maps np.nan (and np.inf) to 0
    out = out.astype('uint8')
    out = Image.fromarray(out, 'RGBA')
    return out


img1 = Image.new('RGBA', size=(100, 100), color=(255, 0, 0, 255))
# draw = ImageDraw.Draw(img1)
# draw.rectangle((33, 0, 66, 100), fill=(255, 0, 0, 128))
# draw.rectangle((67, 0, 100, 100), fill=(255, 0, 0, 0))
# img1.save('/tmp/img1.png')

# img2 = Image.new('RGBA', size=(100, 100), color=(0, 255, 0, 255))
# draw = ImageDraw.Draw(img2)
# draw.rectangle((0, 33, 100, 66), fill=(0, 255, 0, 128))
# draw.rectangle((0, 67, 100, 100), fill=(0, 255, 0, 0))
# img2.save('/tmp/img2.png')

# img3 = alpha_composite(img2, img1)
# img3.save('/tmp/img4.png')

img2 = Image.open('/home/narendra/Documents/pinp/pingeneration/pics/Philips GC1011 1200-Watt Steam Iron (Color May Vary).jpg')
img2 = img2.convert('RGBA')
img = Img(file_path='/tmp/t.jpg')
img.obj  = img2
layer_img_1 = Img.make_blank_img(img_size=(img2.size), folder_path='/tmp/', color=(0, 0, 0,0),transparent=True)
layer_img_1_1 = deepcopy(layer_img_1)
layer_img_2 = Img.make_blank_img(img_size=(500,500), folder_path='/tmp/', color=(255, 255, 0,100),transparent=True)
layer_img_1_1.merge_imgs(layer_img_2,pin_loc=(int(layer_img_1_1.width/2-layer_img_2.width/2),int(layer_img_1_1.height/2-layer_img_2.height/2)))

img3 = alpha_composite(layer_img_1_1.obj,layer_img_1.obj)
img3.save('/tmp/img4.png')
img3.show()
