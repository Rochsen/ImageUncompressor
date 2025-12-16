import os
import sys
import stat
import shutil
import subprocess
from enum import Enum
from logging import basicConfig, INFO, info
from PIL import Image
from typing import Optional, Tuple


basicConfig(level=INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class BANDIZIP_PATHS(Enum):
    """
    Bandizip 安装路径枚举
    """
    BANDIZIP = "Bandizip.exe"
    BANDIZIP_LNK = "C:\\Users\\10291\\Desktop\\Bandizip.exe"
    BANDIZIP_PATH = r"C:\Program Files\Bandizip\Bandizip.exe"
    BANDIZIP_PATH_X86 = r"C:\Program Files (x86)\Bandizip\Bandizip.exe"


class ImageCompressor:
    """
    带密码的分卷图包解压以及分类处理器
        @param input_dir: 输入目录
        @param output_mobile_dir: 移动端图片输出目录
        @param output_pc_dir: PC图片输出目录
        @param allow_clean_empty_dir: 是否允许清理空目录
        @param effect_archive_suffix: 带密码的分卷图包后缀
    """

    def __init__(
            self,
            input_dir: str = "/path/pic",
            output_mobile_dir: str = "/path/saveMobilePaper",
            output_pc_dir: str = "/path/savePcPaper",
            password: str = "https://www.91xiezhen.top",
            allow_clean_empty_dir: bool = True,
            effect_archive_suffix: str = ".7z.001",
    ):
        # 变量初始化
        self.TARGET_DIR = input_dir
        self.PC_PAPER_PATH = output_pc_dir
        self.MOBILE_PAPER_PATH = output_mobile_dir

        # 压缩包密码
        self.passwd = password

        # 分卷图包后缀
        self.effect_archive_suffix = effect_archive_suffix

        # 是否清理空目录
        self.allow_clean_empty_dir = allow_clean_empty_dir

        # 支持的图片格式
        self.SUPPORTED_IMAGE_FORMATS = (".jpg", ".jpeg", ".png")

        # 创建必要的目录
        self._create_output_directories()

    def _create_output_directories(self):
        """创建输出目录"""
        os.makedirs(self.PC_PAPER_PATH, exist_ok=True)
        os.makedirs(self.MOBILE_PAPER_PATH, exist_ok=True)

    @staticmethod
    def find_bandizip() -> Optional[str]:
        """查找系统中的Bandizip程序"""
        # 1. 从PATH中查找
        bandzip_path = shutil.which('Bandizip.exe')
        if bandzip_path and os.path.exists(bandzip_path):
            info(f"方式1找到 Bandizip 程序: {bandzip_path}")
            return bandzip_path

        # 2. 检查常见安装位置
        for path in BANDIZIP_PATHS:
            if os.path.exists(path.value):
                info(f"方式2找到 Bandizip 程序: {bandzip_path}")
                return path.value

        # 3. 尝试在目标目录附近查找
        try:
            # 假设Bandizip可能在脚本同级目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_path = os.path.join(script_dir, "Bandizip.exe")
            if os.path.exists(possible_path):
                info(f"方式3找到 Bandizip 程序: {bandzip_path}")
                return possible_path
        except Exception as e:
            info(f"无法从 PATH 中找到 Bandizip 程序: {e}")
            pass

        return None

    @staticmethod
    def get_image_info(image_path: str) -> (
        Tuple[
            Optional[Image.Image],
            Optional[Tuple[int, int]]
        ]
    ):
        """获取图片信息和尺寸"""
        try:
            with Image.open(image_path) as img:
                return img.copy(), img.size
        except Exception as e:
            info(f"无法打开图片 {image_path}: {e}")
            return None, None

    def process_images(self,
                       unique_label: Optional[str] = None):
        """
        处理图片分类和移动
            @param unique_label: 图片前缀自定义的唯一标识，可选指定
        """
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
                        if unique_label:
                            target_path = os.path.join(
                                self.MOBILE_PAPER_PATH,
                                f"mobile_{unique_label}_{mobile_index:04d}{file_ext}"
                            )
                        else:
                            target_path = os.path.join(
                                self.MOBILE_PAPER_PATH,
                                f"mobile_{mobile_index:04d}{file_ext}"
                            )
                    else:
                        pc_index += 1
                        if unique_label:
                            target_path = os.path.join(
                                self.PC_PAPER_PATH,
                                f"pc_{unique_label}_{pc_index:04d}{file_ext}"
                            )
                        else:
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
                            target_path = (
                                f"{base_name}_{counter:02d}{file_ext}"
                            )
                            counter += 1

                    shutil.move(file_path, target_path)
                    processed_count += 1

                    # 每处理100张图片输出一次进度
                    if processed_count % 100 == 0:
                        info(f"已处理 {processed_count} 张图片...")

                except PermissionError as e:
                    info(f"权限错误: 无法移动文件 {file_path}")
                    info(f"错误详情: {e}")
                    error_count += 1
                except Exception as e:
                    info(f"处理文件 {file_path} 时发生错误: {e}")
                    error_count += 1
                finally:
                    if img:
                        img.close()

        info(f"\n{'='*50}")
        info("处理完成!")
        info(f"总处理图片: {processed_count}")
        info(f"PC图片数量: {pc_index}")
        info(f"移动端图片数量: {mobile_index}")
        info(f"错误数量: {error_count}")
        info(f"{'='*50}")

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
                info(f"已删除空目录: {dir_path}")
            except Exception as e:
                info(f"无法删除目录 {dir_path}: {e}")

        info(f"共清理 {len(empty_dirs)} 个空目录")

    def uncompress_volume(self,
                          archive_path: str,
                          password: str,
                          extract_to: Optional[str] = None,
                          ) -> bool:
        """解压分卷压缩的文件"""
        effect_archive_suffix = self.effect_archive_suffix

        # 验证输入
        if not archive_path.endswith(effect_archive_suffix):
            info(f"错误: 不是有效的分卷压缩文件: {archive_path}")
            return False

        if not os.path.exists(archive_path):
            info(f"错误: 压缩文件不存在: {archive_path}")
            return False

        # 查找Bandizip
        bandzip_exe = self.find_bandizip()
        if not bandzip_exe:
            info("错误: 未找到Bandizip程序")
            info("请确保Bandizip已安装或在以下位置之一:")
            for path in BANDIZIP_PATHS:
                info(f"  - {path.value}")
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

        info(f"开始解压: {os.path.basename(archive_path)}")
        info(f"输出到: {extract_to}")

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
                info("解压成功!")
                return True
            else:
                info(f"解压失败! 返回码: {result.returncode}")
                if result.stderr:
                    info(f"错误输出: {result.stderr[:500]}")  # 只显示前500字符
                return False

        except FileNotFoundError:
            info(f"错误: 无法执行程序 {bandzip_exe}")
            return False
        except Exception as e:
            info(f"解压过程中发生异常: {e}")
            return False

    @staticmethod
    def remove_archive(archive_path: str):
        """删除压缩包所在的目录

        Args:
            archive_path (str): 压缩包路径
        """
        res = os.path.dirname(archive_path)
        try:
            shutil.rmtree(res)
            
        except PermissionError:
            # 递归修改文件夹内所有文件和子文件夹的权限
            
            for root, dirs, files in os.walk(res):
                for d in dirs:
                    os.chmod(os.path.join(root, d), stat.S_IWRITE)
                for f in files:
                    os.chmod(os.path.join(root, f), stat.S_IWRITE)

            # 重新尝试删除
            shutil.rmtree(res)

        except Exception as e:
            info(f"无法删除文件 {res}: {e}")
