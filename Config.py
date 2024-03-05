# -*- coding:utf-8 -*-
# 打包配置
# 说明：
# 1. post_init只会初始化“${}”引用一次
# 2. post_init后设置的变量不会替换“${}”引用，需自行维护
# 3. 默认加载common下面的配置文件
# 4. Game非common目录的文件覆盖旧配置

from . import util
import os
import sys
import re

class Config(object):

    def __init__(self, config_dir="./"):
        self.config_dir = config_dir
        self._env = {}
        self.re_resource_sub_dir = re.compile("resources/((?:\w|\_)+)/")

        if sys.platform == "win32":
            self.set_env("HOMEPATH", "c:" + os.getenv("HOMEPATH"))
        elif sys.platform == "darwin" or sys.platform == "linux2":
            self.set_env("HOMEPATH", os.getenv("HOME"))
        print("HOMEPATH", self.get_env("HOMEPATH"))

        if config_dir is not None:
            self.load(config_dir)

    def load(self, config_dir="./"):
        # load config
        self.config_dir = config_dir
        file_path = self.config_dir + "Config/config.json"
        json_obj = util.load_json(file_path)
        for k in json_obj:
            self._env[k] = json_obj[k]

        # load build platform config
        file_path = "%s/Config/Platform/%s.json" % (self.config_dir, sys.platform)
        if os.path.exists(file_path):
            obj = util.load_json(file_path)
            for k in obj:
                self._env[k] = obj[k]

    def load_config(self, n):
        if n is None:
            n = "dev"
        file_path = "./Config/%s/config.json" % (n)
        print("file_path", file_path)

        if os.path.exists(file_path):
            obj = util.load_json(file_path)
            for k in obj:
                self._env[k] = obj[k]

    def set_use_git(self, used):
        self.use_git = used

    def set_env(self, key, value):
        self._env[key] = value

    def get_env(self, key, strict=True):
        value = self._env.get(key, None)
        if strict:
            assert value is not None, "env value is not valid!! key:%s" % key
        return value

    def post_init(self):
        self._replace_all_env_without_symbols()
        print("config post init succeed.")

    def _replace_all_env_without_symbols(self):
        """
        把${Symbol}变量替换成RunTime值
        :return:
        """
        need_handle_list = []
        for k, v in self._env.iteritems():
            if isinstance(v, str) and "${" in v:
                need_handle_list.append(k)

        nothing_to_delete_count = 0
        while len(need_handle_list):
            delete_list = set()
            for handle_k in need_handle_list:
                handle_v = self._env[handle_k]
                for k, v in self._env.iteritems():
                    if k == handle_k:
                        continue
                    symbol = "${%s}" % k
                    if symbol in handle_v:
                        self._env[handle_k] = handle_v.replace(symbol, str(v))
                    if "${" not in handle_v:
                        delete_list.add(handle_k)
            for delete_k in delete_list:
                nothing_to_delete_count = 0
                need_handle_list.remove(delete_k)
            else:
                nothing_to_delete_count += 1
                # TODO：30 是一个magic number
                if nothing_to_delete_count >= 30:
                    print("not finished", need_handle_list)
                    for nf_k in need_handle_list:
                        print("key", nf_k, self._env[nf_k])
                    raise RuntimeError("replace_all_env_without_symbols failed!")

    def replace_symbols(self, string):
        for k, v in self._env.iteritems():
            symbol = "${%s}" % k
            if symbol in string:
                string = string.replace(symbol, str(v))
        return string