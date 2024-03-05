# -*- encoding:utf-8 -*-

from . import const
from . import Config

class Data(object):

    def __init__(self):
        self.unityPath = './'
        self.projectPath = './'
        # 以上必须初始化
        self.platform = const.PLATFORM_WIN64
        self.logFilePath = "./log.txt"
        self.version = "1.0.1"
        self.ignoreVersions = ""
        self.reviewVersions = ""
        self.config = "dev"
        self.branch = "origin/dev"
        self.release_config = ["release"]
        # res/script忽略文件列表
        self.ignoreFileExts = [
            "assembly_assembly-csharp.assetbundle",
            "assembly_assembly-csharp.assetbundle.manifest",
            ".meta",
            ".DS_Store",
            ".json",
            ".proto",
            ".md",
            ]
        # 热更新资源忽略文件列表，只删除files.json中的文件，目录下的源文件不删除
        self.patchIgnoreFileExts = self.ignoreFileExts + [
            "data_channel.assetbundle",
            "data_channel.assetbundle.manifest",
        ]
        # 是否开发版的包是devsdk模式，true则包名是标准名
        self.dev_sdk = False


    def get_main_version(self):
        numbers = self.version.split(".")
        s = str(numbers[0]) + str(numbers[1])
        return s

    def post_init(self):
        for attr in dir(self):
            value = getattr(self, attr, None)
            if type(value) is str and not attr.startswith("_"):
                setattr(self, attr, self.translate(value))

    def translate(self, input_string):
        for attr in dir(self):
            if not attr.startswith("_"):
                value = getattr(self, attr, None)
                input_string = input_string.replace("${%s}" % attr, str(value))
        return input_string

data = Data()
config = Config.Config()

if __name__ == "__main__":
    data.post_init()
    print(data.logFilePath)