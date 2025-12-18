import os
import stat
import shutil


MOBILE_PIC_PATH = "D:\\BaiduNetdiskDownload\\saveMobilePaper"
TARGET_SIZE = 1772273

# 移动位置
MOBILE_MOVE_PATH = "D:\\BaiduNetdiskDownload\\MOVE_PATH"

os.makedirs(MOBILE_MOVE_PATH, exist_ok=True)


for root, dirs, files in os.walk(MOBILE_PIC_PATH):
    for file in files:
        file_path = os.path.join(root, file)
        file_ext = os.path.splitext(file_path)[-1].lower()
        file_size = os.path.getsize(file_path)

        if file_size == TARGET_SIZE:
            print(file_path)
            # shutil.move(file_path, MOBILE_MOVE_PATH)
            try:
                os.remove(file_path)
            except PermissionError:
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
            