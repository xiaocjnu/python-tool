# -*- encoding:utf-8 -*-
import sys
import zipfile
import os
import shutil
import hashlib
import json
import shutil

class ChDir:

    def __init__(self, chPath):
        self.enteringPath = None
        self.chPath = chPath

    def __enter__(self):
        self.enteringPath = os.getcwd()
        os.chdir(self.chPath)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.enteringPath)

def get_git_dir_version(git_dir):
    """
    返回仓库所有版本的数量
    :return boolean, int: 是否獲取成功，版本號
    """
    result = False
    version = -1
    with ChDir(git_dir):
        cmd = "git rev-list HEAD --count"
        pipe = os.popen(cmd)
        line = pipe.readline()
        try:
            result = True
            version = int(line)
        except Exception as e:
            print((e))
    return result, version


def get_git_version():
    """
    返回仓库所有版本的数量
    :return boolean, int: 是否獲取成功，版本號
    """
    cmd = "git rev-list HEAD --count"
    pipe = os.popen(cmd)
    line = pipe.readline()
    try:
        return True, int(line)
    except Exception as e:
        print((e))
        return False, -1


def dump_json(json_obj, file_path):
    dir_path = os.path.dirname(file_path)
    if len(dir_path) and not os.path.exists(dir_path):
        os.makedirs(dir_path)

    print("dump_json", file_path)
    with open(file_path, 'w') as json_file:
        json.dump(json_obj, json_file, indent = 4)


def load_json(file_path):
    with open(file_path, 'r') as json_file:
        try:
            json_obj = json.load(json_file)
        except Exception as e:
            raise RuntimeError("load json failed! %s \nerr:%s" % (file_path, e))

        assert json_obj

        new_json_obj = {}
        for k in json_obj:
            v = json_obj[k]
            new_k = k
            new_v = v
            if isinstance(v, str):
                new_v = str(v)
            new_json_obj[new_k] = new_v

        # print(new_json_obj)
        return new_json_obj


def make_dir_zip(source_dir, output_filename):
    """
    打包目录为zip文件（未压缩）
    """
    zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
            zipf.write(pathfile, arcname)
    zipf.close()


def unzip(file_path, output_dir):
    """
    解压缩文件
    :param file_path:
    :return:
    """
    zip_file = zipfile.ZipFile(file_path, 'r')
    zip_file.extractall(output_dir)
    zip_file.close()


def git_pull(git_dir):
    with ChangeDir.ChangeDir(git_dir):
        cmd = "git fetch"
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git fetch failed!")
        cmd = "git pull"
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git pull failed!")
        print("git pull succeed!")


def git_show_current_branch_name(git_dir):
    branch_name = None
    with ChangeDir.ChangeDir(git_dir):
        cmd = "git branch --list"
        pipe = os.popen(cmd)
        lines = pipe.readlines()
        for line in lines:
            if line.startswith("* "):
                branch_name = line.replace("* ", "")
                break
    if branch_name is None:
        raise RuntimeError("git show branch failed!")
    return branch_name


def git_show_submodule_current_branch_content(git_dir):
    content = None
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git submodule foreach "git branch --list"'
        pipe = os.popen(cmd)
        content = pipe.read()
    if content is None:
        raise RuntimeError("git show submodule branch failed!")
    return content


def git_reset_submodules(git_dir):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git submodule foreach "git reset --hard HEAD"'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git reset submodules failed! %s" % git_dir)


def git_clean_submodules(git_dir):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git submodule foreach "git clean -fd"'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git clean submodules failed! %s" % git_dir)


def git_reset(git_dir):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git reset --hard HEAD'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git reset failed! %s" % git_dir)


def git_clean(git_dir):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git clean -fd'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git clean failed! %s" % git_dir)


def git_switch_branch(git_dir, branch):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git reset --hard HEAD'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git reset failed! %s" % git_dir)
        cmd = 'git fetch'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git fetch failed! %s" % git_dir)
        cmd = "git checkout %s" % branch
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git switch branch(%s) failed! %s" % (branch, git_dir))


def git_diff_local_remote(git_dir, branch):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git fetch origin'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git fetch failed! %s" % git_dir)

        cmd = "git log %s..origin/%s" % (branch, branch)
        pipe = os.popen(cmd)
        content = pipe.read()
        diff_content = content + "\n"

        cmd = "git diff --stat %s origin/%s" % (branch, branch)
        pipe = os.popen(cmd)
        content = pipe.read()
        diff_content = diff_content + content
    return diff_content


def git_diff_submodules_local_remote(git_dir, branch):
    with ChangeDir.ChangeDir(git_dir):
        cmd = 'git fetch origin'
        ret = os.system(cmd)
        if ret:
            raise RuntimeError("git fetch failed! %s" % git_dir)

        cmd = "git log %s..origin/%s" % (branch, branch)
        pipe = os.popen(cmd)
        content = pipe.read()
        diff_content = content + "\n"

        cmd = "git diff --stat %s origin/%s" % (branch, branch)
        pipe = os.popen(cmd)
        content = pipe.read()
        diff_content = diff_content + content
    return diff_content


# func 参数：文件路径，根目录路径（也就是root）
def walk_file(dirPath, func, rootPath=None):
    if not os.path.exists(dirPath):
        return
    if rootPath is None:
        rootPath = dirPath
    file_names = os.listdir(dirPath)
    for file_name in file_names:
        file_path = os.path.join(dirPath, file_name)
        if os.path.isfile(file_path):
            func(file_path, rootPath)
        elif os.path.isdir(file_path):
            walk_file(file_path, func, rootPath)


# 比较两个对象值是否相同
def compare_object(obj1, obj2):
    type1 = type(obj1)
    type2 = type(obj2)
    if type1 != type2:
        print("unmatch type", type1, type2)
        return False
    if type1 == dict:
        len1 = len(obj1.keys())
        len2 = len(obj2.keys())
        if len1 != len2:
            print("unmatch len", len1, len2)
            return False
        for key, value in obj1.iteritems():
            ret = compare_object(value, obj2.get(key, None))
            if not ret:
                return False
    elif type1 == str:
        return obj1 == obj2
    elif type1 == list:
        len1 = len(obj1)
        len2 = len(obj2)
        if len1 != len2:
            print("unmatch len", len1, len2)
            return False
        for index, value in enumerate(obj1):
            ret = compare_object(value, obj2[index])
            if not ret:
                return False
    elif type1 == set():
        len1 = len(obj1)
        len2 = len(obj2)
        if len1 != len2:
            print("unmatch len", len1, len2)
            return False
        index = 0
        for value in obj1:
            ret = compare_object(value, obj2[index])
            if not ret:
                return False
            index += 1
    return True


def copy_tree(src_dir, dest_dir):
    if not os.path.isdir(src_dir) or not os.path.isdir(dest_dir):
        raise Exception("just operate dir")

    def func(file_path, root):
        rel_path = os.path.relpath(file_path, root)
        dest_path = os.path.join(dest_dir, rel_path)
        temp_dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(temp_dest_dir):
            os.makedirs(temp_dest_dir)
        shutil.copy2(file_path, dest_path)

    walk_file(src_dir, src_dir, func)

def zip(dirPath, zipPath):
    if not os.path.exists(zipPath):
        try:
            os.makedirs(os.path.dirname(zipPath))
        except Exception as e:
            print("zip mkdirs exception", e.message)
    else:
        os.remove(zipPath)
    import zipfile
    f = zipfile.ZipFile(zipPath,'w',zipfile.ZIP_DEFLATED,allowZip64=True)
    with ChDir(dirPath):
        for dirpath, dirnames, filenames in os.walk(dirPath):
            for filename in filenames:
                f.write(os.path.join(os.path.relpath(dirpath, dirPath), filename))
    f.close()


def unzip(zipPath, dirPath):
    with zipfile.ZipFile(zipPath, 'r',zipfile.ZIP_DEFLATED,allowZip64=True) as zf:
        zf.extractall(dirPath)


def readFileSize(filePath):
    size = 0
    with open(filePath, 'rb') as f:
        size += len(f.read())
    return size

def calMD5(filePath):
    with open(filePath, 'rb') as f:
        data = f.read()
    h = hashlib.md5()
    h.update(data)
    return h.hexdigest()

def warpIgnoreVersions(ignoreVersions):
    if ignoreVersions == "" or ignoreVersions == "none":
        return "[]"
    else:
        splits = ignoreVersions.split(",")
        ignoreVersions = map(lambda x: "\"" + str(x) + "\"", splits)
        return "[" + ",".join(ignoreVersions) + "]"
    

def buildFileIndex(destDir, version, ignoreVersions="none", reviewVersions="none", ignoreFileExts=None):
    # os.system("csharp_tools.exe " + destDir)
    
    # fileVersions
    fileVersionsPath = destDir + "/filesVersion.json"
    fileStr = "{"
    fileStr = fileStr + "\t\"Version\":\"" + version + "\","
    fileStr = fileStr + "\n\t\"IgnoreVersions\":" + warpIgnoreVersions(ignoreVersions) + ","
    fileStr = fileStr + "\n\t\"ReviewVersions\":" + warpIgnoreVersions(reviewVersions) + "\n}"
    
    with open(fileVersionsPath, 'w') as f:
        f.write(fileStr)
        
    fileIndexPath = destDir + "/files.json"
    fileStr = "{"
    fileStr = fileStr + "\t\"Version\":\"" + version + "\","
    fileStr = fileStr + "\n\t\"IgnoreVersions\":" + warpIgnoreVersions(ignoreVersions) + ","
    fileStr = fileStr + "\n\t\"ReviewVersions\":" + warpIgnoreVersions(reviewVersions) + ","
    fileStr = fileStr + "\n\t\"Datas\":[ "
    for dirPath, dirnames, filenames in os.walk(destDir):
        for fileName in filenames:
            filePath = dirPath + "/" + fileName
            if ignoreFileExts is not None:
                isignore = False
                for fileExt in ignoreFileExts:
                    if filePath.endswith(fileExt):
                        isignore = True
                        break
                if isignore:
                    print("file ignored:", filePath)
                    continue
            fileStr = fileStr + "\n\t\t{ \"path\":\"" + filePath.replace(destDir, "").replace("\\", "/") + "\"" + ", \"md5\":\"" + calMD5(filePath) + "\"" + ",\"size\":" + str(readFileSize(filePath)) + " },"
    fileStr = fileStr[:-1] + "\n"
    fileStr = fileStr + "\t]"
    fileStr = fileStr + "\n}"

    with open(fileIndexPath, 'w') as f:
        f.write(fileStr)


# 检查是否存在lua文件
def checkLuaFileExists(destDir, minCount=10):
    count = 0
    for dirPath, dirnames, filenames in os.walk(destDir):
        for fileName in filenames:
            if fileName.endswith(".unity3d") and fileName.startswith("lua"):
                count += 1
                if count >= minCount:
                    return True
    print("lua files count is ", count)
    return False

# 检查是否存在res文件
def checkResFileExists(destDir, minCount=10):
    count = 0
    for dirPath, dirnames, filenames in os.walk(destDir):
        for fileName in filenames:
            if fileName.endswith(".assetbundle"):
                count += 1
                if count >= minCount:
                    return True
    print("res files count is ", count)
    return False


def check_python3():
    return os.system("python3 --version") == 0


if __name__ == "__main__":
    zip("F:/Y1/code/trunk/tool_chain/build_client", "F:/Y1/code/trunk/tool_chain//1/1.zip")
    # print(calMD5("F:/Y1/code/trunk/tool_chain//1/1.zip"))
    # print(readFileSize("F:/Y1/code/trunk/tool_chain//1/1.zip"))
    # unzip("F:/Y1/code/trunk/tool_chain//1/1.zip", "F:/Y1/code/trunk/tool_chain/build_client1")
    # unzip("./1/1.zip", "F:/Y1/code/trunk/tool_chain/build_client/2")