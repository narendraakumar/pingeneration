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
    WRITE_TXT = True
    H_LINE = 1
    V_LINE = 1
    L_MARGIN = 50
    R_MARGIN = 50
    B_MARGIN = 30
    if WRITE_TXT:
        V_GAP = 20
        H_GAP = 20
        FONT_SIZE = 20
    else:
        V_GAP = 2
        H_GAP = 2
        FONT_SIZE = 2

    MAX_NUM = 999999999
    HEADER_FONT_SIZE = 60
    T_MARGIN = 10 + HEADER_FONT_SIZE * 2
    DESIRED_HEIGHT = 300
    TOTAL_V_GAP = V_GAP * H_LINE
    TOTAL_H_GAP = H_GAP * H_LINE
    FONT_COLOR = 'rgb(255, 0, 0)'
    FONT_COLOR_HEADER = 'rgb(255, 0, 0)'

