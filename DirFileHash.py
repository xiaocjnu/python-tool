# -*- coding: utf-8 -*-
import os, re
from .util import calMD5

class DirFileHash(object):
    
    def __init__(self) -> None:
        self.ignoreRegs = None

    def collect(self, work_dir, ignoreRegs=None):
        if ignoreRegs is None:
            ignoreRegs = []
        self.ignoreRegs = []
        for reg in ignoreRegs:
            self.ignoreRegs.append(re.compile(reg))
        files_hash = {}
        for root, dirnames, filenames in os.walk(work_dir):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                if self.isIgnore(filepath):
                    continue
                files_hash[os.path.relpath(filepath, work_dir)] = calMD5(filepath)
            for dirname in dirnames:
                dirpath = os.path.join(root, dirname)
                if self.isIgnore(dirpath):
                    dirnames.remove(dirname)
        return files_hash

    def isIgnore(self, filepath):
        for reg in self.ignoreRegs:
            if reg.match(filepath):
                return True
        return False
    
