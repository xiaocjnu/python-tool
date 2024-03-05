# -*- coding: utf-8 -*-
"""
系统指令调用
"""
import sys
import os
import subprocess


def safe_execute_return(cmd):
    print("[SHELL]%s> %s" % (os.getcwd(), cmd))
    r = os.popen(cmd)
    text = r.read()  
    r.close()  
    print("[SHELL]%s" % text)
    return text  

def safe_execute(cmd, msg="", pass_code_list=None, code_callback_dict=None):
    print("[SHELL]%s> %s" % (os.getcwd(), cmd))
    ret = os.system(cmd)
    if code_callback_dict and ret in code_callback_dict:
        code_callback_dict[ret]()
    if ret and (not pass_code_list or (pass_code_list and ret not in pass_code_list)):
        raise RuntimeError("%s:%s失败 code:%s" % (os.getcwd(), msg, ret))
    return ret

def execute(cmd, msg="", code_callback_dict=None):
    print("[SHELL]%s> %s" % (os.getcwd(), cmd))
    ret = os.system(cmd)
    if code_callback_dict and ret in code_callback_dict:
        code_callback_dict[ret]()
    return ret


def safe_execute_subprocess(cmd, msg, pass_code_list=None, code_callback_dict=None):
    print("[SHELL]%s> %s" % (os.getcwd(), cmd))
    sys.stdout.flush()
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stdout, shell=True)
    while p.poll() is None:
        sys.stdout.flush()
    ret = p.returncode
    if code_callback_dict and ret in code_callback_dict:
        code_callback_dict[ret]()
    if ret and (not pass_code_list or (pass_code_list and ret not in pass_code_list)):
        raise RuntimeError("%s:%s失败 code:%s" % (os.getcwd(), msg, ret))
    return ret

