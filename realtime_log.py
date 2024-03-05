# -*- coding: utf-8 -*-

COMMENT = """
 ##############################################
##                                            ##
##            Peilin Kelly Chan               ##
##     <https://github.com/mr-kelly>          ##
##            <23110388@qq.com>               ##
##                                            ##
##     a cross-platform build script for      ##
##  Unity3D console mode realtime log output  ##
##                                            ##
##                                            ##
 ##############################################
"""

import subprocess
import os
import sys
import _thread
import time
from . import tail


def tail_thread(tail_file):
    print("wait for tail file ... %s" % tail_file)
    while True:
        if os.path.exists(tail_file):
            print("Start tail file..... %s" % tail_file)
            break

    t = tail.Tail(tail_file)
    t.register_callback(unity_log_tail)
    t.follow(s=1)


def unity_log_tail(txt):
    print(txt)


def unity_process(cmd, project_path, log_path):
    """
    call unity process to build
    """
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
            print('delete %s' % log_path)
        except Exception as e:
            pass

    # new thread to tail log file
    _thread.start_new_thread(tail_thread, (log_path, ))
    print(cmd)
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, cwd=project_path # stderr=subprocess.STDOUT, cwd=project_path
    )

    while True:
        out = process.stdout.read()
        if out != '':
            sys.stdout.write("[Unity]: " + str(out))
            sys.stdout.flush()
        if process.poll() != None:
            time.sleep(2)
            print("Done! %d" % process.returncode)
            return process.returncode


def fullpath(path):
    return os.path.abspath(os.path.expanduser(path))


if __name__ == "__main__":
    unity_process("dir", "./", "log.txt")