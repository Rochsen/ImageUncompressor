import glob
import shutil
import stat
from os import remove, chmod

list_path_1 = glob.glob(r"D:\BaiduNetdiskDownload\saveMobilePaper\\mobile_*")
num = len(list_path_1)
print("\n".join(list_path_1), num)
for i in list_path_1:
    try:
        remove(i)
    except PermissionError:
        # 修改文件权限后重试
        chmod(i, stat.S_IWRITE)
        remove(i)
    except Exception as e:
        print(f"无法删除文件 {i}: {e}")


list_path_2 = glob.glob(r"D:\BaiduNetdiskDownload\savePcPaper\\pc_*")
num = len(list_path_2)

print("\n".join(list_path_2), num)

for i in list_path_2:
    try:
        remove(i)
    except PermissionError:
        # 修改文件权限后重试
        chmod(i, stat.S_IWRITE)
        remove(i)
    except Exception as e:
        print(f"无法删除文件 {i}: {e}")
