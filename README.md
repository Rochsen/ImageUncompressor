仅个人学习记录，请勿用于商业用途

## 项目结构
```code
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        2025/12/13     16:16                .venv
d-----        2025/12/15     22:40                bk
-a----        2025/12/13     19:14              6 .gitignore
-a----        2025/12/13     15:28              5 .python-version
-a----        2025/12/15     22:35          10789 parse.py
-a----        2025/12/13     16:26            277 pyproject.toml
-a----        2025/12/15     22:40            935 README.md
-a----        2025/12/14     23:42           9581 test.py
-a----        2025/12/13     16:26          25392 uv.lock
```

## 使用方法
```python

# 自行调用封装的类函数，具体查看test.py

from parse import ImageCompressor

compressor = ImageCompressor(
            input_dir="/path/to/your/7z/dirname/",
            output_mobile_dir="/path/to/save/portrait/pic",
            output_pc_dir="/path/to/save/nois_portrait/pic",
            allow_clean_empty_dir=True,
            effect_archive_suffix=".7z.001"
            )

```
