import os


def get_abs_path(rel_path:str):
    """
    :param rel_path: its relative path to project  dir
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path + rel_path
