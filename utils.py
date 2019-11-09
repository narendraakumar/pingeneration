import os


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


