from parse import ImageCompressor
from typing import Dict
import os
import sys
import glob
import re
import shutil
import stat

NUMBER_MATCH = re.compile(r"(No\.)?(\d{3,4})")


def dry_run_func(compressor) -> Dict:
    """测试运行, 只做路径查找和简单统计或匹配"""

    # 搜索方法
    dry_result = glob.glob(os.path.join(
        compressor.TARGET_DIR, "*", f"*{compressor.effect_archive_suffix}"))
    # 搜索统计
    res_num = len(dry_result)
    print(f"找到分卷文件: {dry_result}, \n数量有{res_num}")

    # 提取图包期数
    issue_list = []

    for p in dry_result:
        match_issue_index = re.search(NUMBER_MATCH, p).group(0)
        issue_list.append(match_issue_index)

    print(issue_list)

    # 返回期数和文件路径映射
    return dict(zip(issue_list, dry_result))


def main(dry_run=False) -> None:
    """主运行函数"""

    try:
        # 创建图片处理对象
        compressor = ImageCompressor(
            input_dir="D:\\BaiduNetdiskDownload\\pickk",
            output_mobile_dir="D:\\BaiduNetdiskDownload\\saveMobilePaper",
            output_pc_dir="D:\\BaiduNetdiskDownload\\savePcPaper",
            allow_clean_empty_dir=True,
            effect_archive_suffix=".7z.001"
        )

        # 步骤1: 查找分卷文件
        print("1. 解压分卷压缩文件...")
        archive_path = ""

        # 测试路径查找
        if dry_run:
            archive_paths = dry_run_func(compressor=compressor)
            for issue_index, archive_path in archive_paths.items():
                res = (os.path.dirname(archive_path))
                print(res)

        else:
            password = "https://www.91xiezhen.top"

            # 测试路径映射
            archive_paths = dry_run_func(compressor=compressor)

            # 循环遍历处理
            for issue_index, archive_path in archive_paths.items():
                if os.path.exists(archive_path):
                    compressor.uncompress_volume(archive_path, password)
                else:
                    print(f"未找到压缩文件: {archive_path}")

                # 步骤2: 清理空目录
                print("2. 清理空目录...")
                compressor.clean_empty_dirs()

                # 步骤3: 处理图片
                print("3. 处理图片分类...")
                compressor.process_images(issue_index)

                # 步骤4: 删除压缩包
                print("4. 删除路径")
                compressor.remove_archive(archive_path)

            print("所有操作完成!")

    except KeyboardInterrupt:
        print("用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main(False)
