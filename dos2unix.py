# -*- coding:utf-8 -*-

import argparse
from . import util
from . import SystemCommand

parser = argparse.ArgumentParser(description='file path')
parser.add_argument('srcDir', type=str, help='file path')


def convert_file(file_path, root):
    if not file_path.endswith(".lua"):
        return
    cmd = "dos2unix %s" % file_path
    SystemCommand.safe_execute(cmd, "convert")


if __name__ == '__main__':
    args = parser.parse_args()

    srcDir = args.srcDir

    util.walk_file(srcDir, convert_file)

