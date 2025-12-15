import os
import sys
from PIL import Image
import shutil
import subprocess
from typing import Optional, Tuple


class ImageCompressor:
    def __init__(self):
        # 初始化路径
        self.BANDZIP_PATHS = [
            r"C:\Program Files\Bandizip\Bandizip.exe",
            r"C:\Program Files (x86)\Bandizip\Bandizip.exe",
            r"Bandizip.exe"
        ]

        self.TARGET_DIR = "D:\\BaiduNetdiskDownload\\pickk"
        self.PC_PAPER_PATH = "D:\\BaiduNetdiskDownload\\savePcPaper"
        self.MOBILE_PAPER_PATH = "D:\\BaiduNetdiskDownload\\saveMobilePaper"

        # 支持的图片格式
        self.SUPPORTED_IMAGE_FORMATS = (
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")

        # 创建必要的目录
        self._create_directories()

    def _create_directories(self):
        """创建必要的目录"""
        os.makedirs(self.PC_PAPER_PATH, exist_ok=True)
        os.makedirs(self.MOBILE_PAPER_PATH, exist_ok=True)

    def find_bandizip(self) -> Optional[str]:
        """查找系统中的Bandizip程序"""
        # 1. 从PATH中查找
        bandzip_path = shutil.which('Bandizip.exe')
        if bandzip_path and os.path.exists(bandzip_path):
            print(f"方式1找到 Bandizip 程序: {bandzip_path}")
            return bandzip_path

        # 2. 检查常见安装位置
        for path in self.BANDZIP_PATHS:
            if os.path.exists(path):
                print(f"方式2找到 Bandizip 程序: {bandzip_path}")
                return path

        # 3. 尝试在目标目录附近查找
        try:
            # 假设Bandizip可能在脚本同级目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_path = os.path.join(script_dir, "Bandizip.exe")
            if os.path.exists(possible_path):
                print(f"方式3找到 Bandizip 程序: {bandzip_path}")
                return possible_path
        except:
            pass

        return None

    def get_image_info(self, image_path: str) -> Tuple[Optional[Image.Image], Optional[Tuple[int, int]]]:
        """获取图片信息和尺寸"""
        try:
            with Image.open(image_path) as img:
                return img.copy(), img.size
        except Exception as e:
            print(f"无法打开图片 {image_path}: {e}")
            return None, None

    def process_images(self):
        """处理图片分类和移动"""
        pc_index = 0
        mobile_index = 0
        processed_count = 0
        error_count = 0

        for root, dirs, files in os.walk(self.TARGET_DIR):
            for file in files:
                # 检查文件扩展名
                if not file.lower().endswith(self.SUPPORTED_IMAGE_FORMATS):
                    continue

                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file_path)[-1].lower()

                # 获取图片信息
                img, size = self.get_image_info(file_path)
                if img is None or size is None:
                    error_count += 1
                    continue

                # 根据宽高比分类
                is_portrait = size[0] <= size[1]  # 竖屏图片

                try:
                    if is_portrait:
                        mobile_index += 1
                        target_path = os.path.join(
                            self.MOBILE_PAPER_PATH,
                            f"mobile_{mobile_index:04d}{file_ext}"
                        )
                    else:
                        pc_index += 1
                        target_path = os.path.join(
                            self.PC_PAPER_PATH,
                            f"pc_{pc_index:04d}{file_ext}"
                        )

                    # 确保目标文件不存在
                    if os.path.exists(target_path):
                        # 如果文件已存在，使用递增编号
                        base_name = os.path.splitext(target_path)[0]
                        counter = 1
                        while os.path.exists(target_path):
                            target_path = f"{base_name}_{counter:02d}{file_ext}"
                            counter += 1

                    shutil.move(file_path, target_path)
                    processed_count += 1

                    # 每处理100张图片输出一次进度
                    if processed_count % 100 == 0:
                        print(f"已处理 {processed_count} 张图片...")

                except PermissionError as e:
                    print(f"权限错误: 无法移动文件 {file_path}")
                    print(f"错误详情: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"处理文件 {file_path} 时发生错误: {e}")
                    error_count += 1
                finally:
                    if img:
                        img.close()

        print(f"\n{'='*50}")
        print(f"处理完成!")
        print(f"总处理图片: {processed_count}")
        print(f"PC图片数量: {pc_index}")
        print(f"移动端图片数量: {mobile_index}")
        print(f"错误数量: {error_count}")
        print(f"{'='*50}")

    def clean_empty_dirs(self):
        """清理空目录（从下往上）"""
        empty_dirs = []

        # 收集所有空目录
        for root, dirs, files in os.walk(self.TARGET_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    empty_dirs.append(dir_path)

        # 删除空目录
        for dir_path in empty_dirs:
            try:
                os.rmdir(dir_path)
                print(f"已删除空目录: {dir_path}")
            except Exception as e:
                print(f"无法删除目录 {dir_path}: {e}")

        print(f"共清理 {len(empty_dirs)} 个空目录")

    def uncompress_volume(self, archive_path: str, password: str,
                          extract_to: Optional[str] = None) -> bool:
        """解压分卷压缩文件"""
        # 验证输入
        if not archive_path.endswith(".7z.001"):
            print(f"错误: 不是有效的分卷压缩文件: {archive_path}")
            return False

        if not os.path.exists(archive_path):
            print(f"错误: 压缩文件不存在: {archive_path}")
            return False

        # 查找Bandizip
        bandzip_exe = self.find_bandizip()
        if not bandzip_exe:
            print("错误: 未找到Bandizip程序")
            print("请确保Bandizip已安装或在以下位置之一:")
            for path in self.BANDZIP_PATHS:
                print(f"  - {path}")
            return False

        # 设置输出目录
        if extract_to is None:
            extract_to = os.path.dirname(archive_path)

        # 创建输出目录
        os.makedirs(extract_to, exist_ok=True)

        # 构建解压命令
        cmd = [
            bandzip_exe,
            'x',           # 解压
            f'-p:{password}',  # 密码
            '-y',          # 全部确认
            f'-o:{extract_to}',  # 输出目录
            '-aoa',        # 覆盖所有文件
            archive_path
        ]

        print(f"开始解压: {os.path.basename(archive_path)}")
        print(f"输出到: {extract_to}")

        try:
            # 使用subprocess.run获取更详细的信息
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode == 0:
                print("解压成功!")
                return True
            else:
                print(f"解压失败! 返回码: {result.returncode}")
                if result.stderr:
                    print(f"错误输出: {result.stderr[:500]}")  # 只显示前500字符
                return False

        except FileNotFoundError:
            print(f"错误: 无法执行程序 {bandzip_exe}")
            return False
        except Exception as e:
            print(f"解压过程中发生异常: {e}")
            return False

    def run(self):
        """主运行函数"""
        print("=" * 60)
        print("图片分类与压缩工具")
        print("=" * 60)

        # 步骤1: 解压分卷文件
        print("\n1. 解压分卷压缩文件...")
        archive_path = os.path.join(self.TARGET_DIR, "063", "063.7z.001")
        password = "https://www.91xiezhen.top"

        if os.path.exists(archive_path):
            self.uncompress_volume(archive_path, password)
        else:
            print(f"未找到压缩文件: {archive_path}")

        # 步骤2: 清理空目录
        print("\n2. 清理空目录...")
        self.clean_empty_dirs()

        # 步骤3: 处理图片
        print("\n3. 处理图片分类...")
        self.process_images()

        print("\n所有操作完成!")


if __name__ == "__main__":
    try:
        compressor = ImageCompressor()
        compressor.run()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行出错: {e}")
        sys.exit(1)
