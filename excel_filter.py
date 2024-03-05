import os
import shutil


def filter_copy(excelPath, workExcelPath, branch):
    if os.path.exists(workExcelPath):
        shutil.rmtree(workExcelPath)
    os.makedirs(workExcelPath)
    files = os.listdir(excelPath)
    file_dir_map = {}
    for file in files:
        file_path = os.path.join(excelPath, file)
        if not os.path.isdir(file_path):
            continue
        if file == branch:
            files2 = os.listdir(os.path.join(excelPath, file))
            for file2 in files2:
                file2_path = os.path.join(excelPath, file, file2)
                if os.path.isfile(file2_path) and file2.endswith(".xlsx") and not file2.startswith("~$"):
                    shutil.copy2(file2_path, workExcelPath)
                    file_dir_map[file2] = file

    for file in files:
        file_path = os.path.join(excelPath, file)
        if (not file in file_dir_map) and os.path.isfile(file_path) and file.endswith(".xlsx") and not file.startswith("~$"):
            shutil.copy2(file_path, workExcelPath)
            file_dir_map[file] = "."
    return file_dir_map
