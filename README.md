# 小巧思（wish Tools）

「微室」的一些小巧思源码。展示在 leewish.xyz 和 (???)leewish.xyz 的「小巧思」页。

## 收录内容

| 文件 | 是什么 | 在线使用 |
| --- | --- | --- |
| `sprite2gif.html` | 精灵图（动作分解图）→ GIF 工具 | 站内提供在线版 |
| `periodic_table.py` | A3 元素周期表生成器（可打印） | 下载后本地运行 |
| `folder_launcher.py` | 文件夹快捷启动器（Windows 小工具） | 下载后本地运行 |

## sprite2gif.html —— 精灵图转 GIF 工具

把角色的"动作分解图"（单列 / 单行 / 多行×多列网格）一键合成循环播放的 GIF。

- 自动识别帧数与网格；细武器 / 特效跨行不粘连
- 智能去背（边缘漫水，不会误伤白色衣物）；帧延时、放大倍数、播放方向可调
- 支持批量：一次拖入多张图、逐组导出
- 单文件、免安装、免上传：全程本地处理，断网也能用
- 用法：用 Chrome / Edge 打开 → 拖入 / 粘贴图片 → 选动作 → 生成 → 下载

## periodic_table.py —— A3 元素周期表生成器

生成 A3 横向（420 × 297 mm）可打印的元素周期表：PDF + PNG。

- 内容：原子序数、中文名、元素符号、英文名、电子排布（惰性气体原子实缩写）、相对原子质量
- 版式：周期 1–7、新旧族号（IA…VIIIA 与 1–18）、s / d / p / f 区标注、镧系 / 锕系独立两行、按族着色图例
- 依赖：matplotlib（`pip install matplotlib`）
- 用法：`python periodic_table.py`，脚本同目录生成 `periodic_table_A3.pdf` 与 `.png`
- 打印：A3 横向、缩放 100%、彩色
- 中文名自动匹配系统字体；如个别字缺字形，可安装 Noto Sans CJK

## folder_launcher.py —— 文件夹快捷启动器

把常用文件夹收进一个小窗口：单击即开，再也不用一层层翻路径（Windows）。

- 主界面是一列文件夹按钮，单击即在资源管理器打开；「＋ 添加文件夹」选择目录，「按名称排序」一键整理
- 装了可选组件 tkinterdnd2 还能直接把文件夹拖进窗口（`pip install tkinterdnd2`）
- 右键快捷方式：打开 / 重命名（仅改显示名）/ 复制路径 / 删除（不会删除磁盘上的文件夹）
- 数据保存在 `folders.json`：优先放 exe 同目录（整个文件夹拷贝即携带）；目录不可写时自动退回 `%APPDATA%`
- 依赖：Python 自带 tkinter，无需安装
- 用法：`python folder_launcher.py`
- 打包：先 `pip install pyinstaller`，再 `pyinstaller --onefile --windowed --clean --name FolderLauncher folder_launcher.py`（装了 tkinterdnd2 追加 `--collect-all tkinterdnd2`），成品可固定到任务栏 / 开始菜单



## 说明

仅供学习交流，转载请注明出处。
