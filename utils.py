import os
from enum import Enum


def get_abs_path(rel_path: str):
    """
    :param rel_path: its relative path to project  dir
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path + rel_path


def write_to_file(file_path, data):
    with open(file_path, 'w') as f:
        for item in data:
            f.write("%s\n" % item)
    return True


def read_from_file(file_path):
    with open(file_path) as f:
        res = f.read()
    return res.split('\n')


class pinproperties(Enum):
    WRITE_TXT = False
    H_LINE = 1
    V_LINE = 1
    L_MARGIN = 50
    R_MARGIN = 50
    B_MARGIN = 30
    MAX_VAL = 9999999999999
    if WRITE_TXT:
        V_GAP = 20
        H_GAP = 20
        FONT_SIZE = 20
        MAX_WIDTH_FOR_TXT = 150  # when text is written to image
    else:
        V_GAP = 2
        H_GAP = 1
        FONT_SIZE = 0
        MAX_WIDTH_FOR_TXT = 1

    MAX_NUM = 999999999
    HEADER_FONT_SIZE = 60
    T_MARGIN = 10
    DESIRED_HEIGHT = 300
    TOTAL_V_GAP = V_GAP * H_LINE
    TOTAL_H_GAP = H_GAP * H_LINE
    FONT_COLOR = 'rgb(255, 0, 0)'
    FONT_COLOR_HEADER = 'rgb(0, 0, 245)'
    V_ALLIGN = True
