import os
from PIL import Image
import shutil
import subprocess


BANDZIP = r"Bandizip.exe"
BANDZIP_LNK = r"C:\Users\10291\Desktop\Bandizip.exe"

TARGET_DIR = "D:\\BaiduNetdiskDownload\\pickk"

PC_PAPER_PATH = "D:\\BaiduNetdiskDownload\\savePcPaper"
MOBILE_PAPER_PATH = "D:\\BaiduNetdiskDownload\\saveMobilePaper"

os.makedirs(PC_PAPER_PATH, exist_ok=True)
os.makedirs(MOBILE_PAPER_PATH, exist_ok=True)


def find_bandizip():
    """查找系统中的Bandizip程序"""
    # 先尝试从PATH中查找
    bandzip_path = shutil.which('Bandizip.exe')
    if bandzip_path:
        return bandzip_path

    # 如果PATH中找不到，检查常见安装位置
    common_paths = [
        r"C:\Program Files\Bandizip\Bandizip.exe",
        r"C:\Program Files (x86)\Bandizip\Bandizip.exe"
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return None


def main():
    """主函数：遍历目标目录中的图片文件并分类移动"""

    # 图片名称索引
    pcpic_index = 0
    mbpic_index = 0
    exc_count = 0

    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            # 获取图片的尺寸
            if file_path.endswith((".jpg", ".png", ".jpeg", ".gif")):
                img_suffix = os.path.splitext(file_path)[-1]

                # 获取图片的尺寸
                img_obj = Image.open(file_path)
                img_ruler = img_obj.size
                img_obj.close()

                img_name = os.path.splitext(file)[0]
                print(file_path, img_name, img_suffix, img_ruler, )

                # 长比宽小（竖屏图片）
                if img_ruler[0] <= img_ruler[1]:
                    try:
                        mbpic_index += 1
                        target_path = os.path.join(
                            MOBILE_PAPER_PATH, f"{mbpic_index}{img_suffix}")
                        shutil.move(file_path, target_path)
                    except PermissionError as e:
                        print(f"权限错误：无法移动文件 {file_path} 到 {target_path}")
                        print(f"详细信息：{e}")
                        # 可以选择跳过该文件或记录日志
                        break

                # 长比宽大（横屏图片）
                else:
                    try:
                        pcpic_index += 1
                        target_path = os.path.join(
                            PC_PAPER_PATH, f"{pcpic_index}{img_suffix}")
                        shutil.move(file_path, target_path)
                    except PermissionError as e:
                        print(f"权限错误：无法移动文件 {file_path} 到 {target_path}")
                        print(f"详细信息：{e}")
                        # 可以选择跳过该文件或记录日志
                        break

                exc_count += 1

    print("已处理图片数量：", exc_count)


def cleanEmptyDir():
    """清理空目录"""
    for root, dirs, files in os.walk(TARGET_DIR):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"已删除空目录：{dir_path}")


def uncompress_file(archive_path, password):
    """解压指定的分卷压缩文件"""
    # 查找Bandizip程序
    bandzip_exe = find_bandizip()
    if not bandzip_exe:
        print("警告: Bandizip程序未找到")
        return False

    if not os.path.exists(archive_path):
        print(f"警告: 压缩文件未找到: {archive_path}")
        return False

    # 确保是.7z.001文件
    if not archive_path.endswith(".7z.001"):
        print(f"警告: 不是有效的分卷压缩文件: {archive_path}")
        return False

    # 直接使用找到的程序路径
    output_dir = os.path.dirname(archive_path)
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        bandzip_exe,  # 使用实际找到的路径
        'x',
        f'-p{password}',
        '-y',
        f'-o{output_dir}',
        archive_path
    ]

    try:
        print(f"开始解压分卷文件: {archive_path}")
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.call(cmd)

        if result == 0:
            print(f"分卷解压完成: {archive_path}")
            return True
        else:
            print(f"分卷解压失败，返回码: {result}")
            return False

    except Exception as e:
        print(f"分卷解压异常: {e}")
        return False


# 在main函数中调用
if __name__ == "__main__":
    # 解压分卷压缩文件
    archive_path = os.path.join(TARGET_DIR, "063", "063.7z.001")
    password = "https://www.91xiezhen.top"
    uncompress_file(archive_path, password)

    # 执行图片分类处理
    # cleanEmptyDir()
    # main()

    # 示例移动单个文件
    # shutil.move(
    #     "D:\\BaiduNetdiskDownload\\pickk\\061\\けん研(けんけん) – NO.061 2023年11月[166P-5V-750.3M]\\2343349_11月vzfeaz\\3984306_ムチムチ×ニットぐらびあ__\\01.jpg",
    #     os.path.join(MOBILE_PAPER_PATH, "1.jpg"))
