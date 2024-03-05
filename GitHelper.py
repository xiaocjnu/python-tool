# -*- coding:utf-8 -*-
# Git操作辅助模块
import os
import sys
from .util import ChDir
from subprocess import Popen, PIPE
from . import SystemCommand
import shutil


def get_head_commit_id(git_dir):
    """
    获取目录下的最新一次提交CommitID
    :param git_dir:
    :return:
    """
    with ChDir(git_dir):
        cmd = "git rev-parse HEAD"
        pipe = os.popen(cmd)
        content = pipe.read()
        return content.replace("\n", "")


def get_change_log(git_dir, old_commit_id, new_commit_id):
    """
    获取旧提交到新提交直接的变更日志
    :param git_dir:
    :param old_commit_id:
    :param new_commit_id:
    :return:
    """
    # 数据可能已经脏了，兼容一下
    old_commit_id = old_commit_id.replace("\n", "")
    new_commit_id = new_commit_id.replace("\n", "")
    with ChDir(git_dir):
        if sys.platform == 'win32':
            process = Popen(["git", "log", "%s...%s" % (old_commit_id, new_commit_id), "--pretty=oneline"],
                            stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            content = stdout.decode('utf-8')
        else:
            cmd = "git log %s...%s --pretty=oneline" % (old_commit_id, new_commit_id)
            print(cmd)
            pipe = os.popen(cmd)
            content = pipe.read()
        return content


def get_change_log_to_head(git_dir, old_commit_id):
    """
    获取旧提交到最新提交直接的变更日志
    :param git_dir:
    :param old_commit_id:
    :return:
    """
    # 数据可能已经脏了，兼容一下
    old_commit_id = old_commit_id.replace("\n", "")
    with ChDir(git_dir):
        if sys.platform == 'win32':
            process = Popen(["git", "log", "%s...HEAD" % old_commit_id, "--pretty=oneline"], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            content = stdout.decode('utf-8')
        else:
            cmd = "git log %s...HEAD --pretty=oneline" % old_commit_id
            print(cmd)
            pipe = os.popen(cmd)
            content = pipe.read()
        return content


def get_project_head_commit_id(git_dir):
    data = {}
    data['Lobby'] = get_head_commit_id(git_dir)

    from Core import Global
    resources_dir = Global.pack_config.get_env("ProjectResourcesDir")
    submodules_name = Global.pack_config.get_env("SUBMODULES_NAME")
    for submodule in submodules_name:
        submodule_dir = "%s/%s/" % (resources_dir, submodule)
        data[submodule] = get_head_commit_id(submodule_dir)
    return data


def get_project_change_log(git_dir, old_commit_data):
    data = {}
    if old_commit_data:
        old_commit_id = old_commit_data['Lobby']
        print("Lobby old_commit_id:", old_commit_id)
        content = get_change_log_to_head(git_dir, old_commit_id)
        print("content:", content)
        data['Lobby'] = content
    else:
        data['Lobby'] = "第一次"

    from Core import Global
    resources_dir = Global.pack_config.get_env("ProjectResourcesDir")
    submodules_name = Global.pack_config.get_env("SUBMODULES_NAME")
    for submodule in submodules_name:
        submodule_dir = "%s/%s/" % (resources_dir, submodule)
        if old_commit_data:
            old_commit_id = old_commit_data.get(submodule, "HEAD")
            print(submodule, " old_commit_id:", old_commit_id)
            content = get_change_log_to_head(submodule_dir, old_commit_id)
            print("content:", content)
            data[submodule] = content
        else:
            data[submodule] = "第一次"
    return data


def switch_branch(git_dir_path, branch):
    """
    切换分支
    :param git_dir_path:
    :return:
    """
    # pull submodules
    with ChDir(git_dir_path):
        callbacks = {}
        def _code256():
            SystemCommand.safe_execute("git checkout -b %s" % branch, "创建新分支:%s" % branch)
            SystemCommand.safe_execute("git push --set-upstream origin %s" % branch, "推送新分支到远端:%s" % branch)
        callbacks[256] = _code256
        SystemCommand.safe_execute("git checkout %s" % branch, "切换分支:%s" % branch, [256], callbacks)
        SystemCommand.safe_execute('git submodule foreach "git checkout %s || true"' % branch, "切换子模块分支:%s" % branch)
    sync(git_dir_path)


def sync(git_dir_path):
    """
    同步本地仓库和远端仓库
    :param git_dir_path:
    :return:
    """
    with ChDir(git_dir_path):
        SystemCommand.safe_execute("git clean -fd", "本地清理unstaged")
        SystemCommand.safe_execute("git reset --hard HEAD", "本地清理staged")
        SystemCommand.safe_execute("git pull", "本地拉取并合并远程仓库", [256])
        SystemCommand.safe_execute('git submodule foreach "git pull"', "本地子模块拉取并合并远程仓库")


def commit_push_dir_to_remote(git_dir_path, commit_msg):
    """
    提交并推送到远程仓库
    :param git_dir_path:
    :param commit_msg:
    :return:
    """
    with ChDir(git_dir_path):
        SystemCommand.safe_execute("git add *", "添加当前目录所有文件")
        SystemCommand.safe_execute('git commit -m "%s"' % commit_msg, "提交到本地仓库", [256, 32768])
        SystemCommand.safe_execute("git push", "推送到远程仓库", [32768])


ignoreWords = ["bug", "fix", "temp", "tmp"]
def get_remote_branchs(git_dir_path):
    """
    获取远端分支列表
    """
    with ChDir(git_dir_path):
        text = SystemCommand.safe_execute_return("git branch -r")
        lines = text.split("\n")
        print(lines)
        branchs = []
        for line in lines:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            line = line.strip()
            if line.startswith("origin/") and not line == "origin/master":
                ignored = False
                for w in ignoreWords:
                    if w in line:
                        ignored = True
                        break
                if not ignored:
                    branchs.append(line.replace("origin/", ""))
    return branchs


def git_remove_dir_files(git_dir_path):
    """
    清空git的一个目录
    :param git_dir_path:
    :return:
    """
    file_or_dirs = os.listdir(git_dir_path)
    for file_name in file_or_dirs:
        path = os.path.join(git_dir_path, file_name)
        if not file_name.startswith("."):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


def copytree(src, dest):
    if not os.path.isdir(src) and os.path.isdir(dest):
        raise StandardError("src/dest 都必须是目录。src:%s dest:%s" % (src, dest))
    file_or_dirs = os.listdir(src)
    for file_name in file_or_dirs:
        src_path = os.path.join(src, file_name)
        dest_path = os.path.join(dest, file_name)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
        else:
            shutil.copytree(src_path, dest_path)


if __name__ == "__main__":
    sys.path.append("../")
    get_remote_branchs("H:/work/hbx/ro/git/server/server/actorserver")