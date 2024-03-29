# -*- coding:utf-8 -*-
# svn操作辅助模块
import os
import sys
from .util import ChDir


def get_revision(svndir):
    """
    获取目录下的最新一次提交Revision
    :param svndir:
    :return:
    """
    with ChDir(svndir):
        cmd = "svn info"
        pipe = os.popen(cmd)
        content = pipe.read()

        lines = content.split("\n")
        for line in lines:
            if line.startswith("Last Changed Rev: "):
                return line.replace("Last Changed Rev: ", "").lstrip().rstrip()
        return ""
    
def get_last_changed_date(svndir):
    """
    获取目录下的最新一次提交日期
    :param svndir:
    :return:
    """
    with ChDir(svndir):
        cmd = "svn info"
        pipe = os.popen(cmd)
        content = pipe.read()

        lines = content.split("\n")
        for line in lines:
            if line.startswith("Last Changed Date: "):
                line = line.split("(")[0]
                return line.replace("Last Changed Date: ", "").lstrip().rstrip()
        return ""
    
def svnupgrade(svndir):
    with ChDir(svndir):
        cmd = "svn upgrade"
        os.popen(cmd)


def get_rep_revision(svndir):
    """
    获取目录下的最新一次提交Revision
    :param svndir:
    :return:
    """
    with ChDir(svndir):
        cmd = "svn info"
        pipe = os.popen(cmd)
        content = pipe.read()

        lines = content.split("\n")
        for line in lines:
            if line.startswith("Revision: "):
                return line.replace("Revision: ", "").lstrip().rstrip()
        return ""

