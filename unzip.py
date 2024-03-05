# -*- encoding:utf-8 -*-

from . import util
import argparse

parser = argparse.ArgumentParser(description='file path')
parser.add_argument('-srcFile', type=str, help='file path')
parser.add_argument('-destDir', type=str, help='file dir')

if __name__ == '__main__':
    args = parser.parse_args()
    util.unzip(args.srcFile, args.destDir)
    exit(0)