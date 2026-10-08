# 小巧思（wish Tools）

「微室」的一些小巧思源码。展示在 leewish.xyz 和 (???)leewish.xyz 的「小巧思」页。

## 收录内容

| 文件 | 是什么 | 在线使用 |
| --- | --- | --- |
| `sprite2gif.html` | 精灵图（动作分解图）→ GIF 工具 | 站内提供在线版 |
| `periodic_table.py` | A3 元素周期表生成器（可打印） | 下载后本地运行 |
| `folder_launcher.py` | 文件夹快捷启动器（Windows 小工具） | 下载后本地运行 |
| `ocr-center/` | 书籍数字化工具集（PDF↔图片、OCR 转 Markdown） | 下载后本地运行 |
| `sd-tools/` | SD 素材工具链（RPG Maker 像素素材） | 下载后本地运行 |
| `folder_size.bat` | 文件夹大小排序器（Windows） | 下载后本地运行 |

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

## ocr-center/ —— 书籍数字化工具集

把纸质书 / 扫描版 PDF 变成可编辑文稿的一套 Windows 小工具：PDF 与图片互转、OCR 转 Markdown（公式、表格、版面尽量保留）。

- 「OCR 中心」`ocr_center.pyw`：图形界面一站式完成 —— ① PDF→图片 ② 图片→PDF ③ OCR→Markdown ④ 全自动流水线（单个 / 批量均可）
- 三个 worker 脚本：`pdf2png_worker.py`、`img2pdf_worker.py`、`ocr_worker.py`（界面与 .bat 都调用它们，也可单独命令行使用）
- 三个快捷入口：`pdf_to_png.bat`、`img_to_pdf.bat`、`ocr_latex.bat`（命令行菜单，不想开图形界面时用）
- 输出统一到本文件夹的 `output\`：分 `pdf-to-png` / `img-to-pdf` / `ocr` 三个子文件夹；可用环境变量 `OCR_OUT_ROOT` 更换位置
- 解释器查找顺序：环境变量 `OCR_PYTHON` → 本文件夹下 `.venv` / `venv` → 系统 Python
- 安装：`pip install pypdfium2 pillow python-docx`；OCR 功能另需 PaddleX（PaddleOCR-VL 产线，首次运行自动下载模型，建议 NVIDIA 显卡环境）
- 用法：下载本文件夹 → 在装好依赖的环境中双击 `ocr_center.pyw`
- 提示：OCR 推理比较吃显存，运行前建议退出其它占用显存的程序
- 从零安装教程（Python / PaddleX 配置全流程）：[ocr-center/install_guide.md](ocr-center/install_guide.md)

## sd-tools/ —— SD 素材工具链

面向 RPG Maker 像素素材的一套本地 AI 生产工具链：文生图 / 重绘 / 草图法出图，去底、拼装、质检一条龙，配套完整风格库文档。个人项目，开发中途暂停；已完成工具链可独立复用。

- 生成三件：`sd_gen.py`（文生图）、`sd_img2img.py`（参考图重绘）、`sd_cn.py`（ControlNet 草图法，跑完自动存 info.json 可验证）
- 行走图线：`chroma_remove.py` / `remove_bg.py`（去底）、`fill_holes.py`（补洞）、`make_sheet.py`（拼 3×4 行走图，48 / 96px）
- 图块线：`tile_pack.py`（拼 768×768 图块表）、`tile_quant.py`（限量色）、`tile_qa.py`（逐格体检）、`tile_zoom.py`（格子放大目检）
- 风格库 `style_guide.md`：底模 / LoRA 分工、提示词与参数基准、三大生产流程、质检体系与踩坑记录（建议先读）
- `examples/`：4 份任务模板（行走 / 高清行走 / 纹理 / 物件）＋ 草图范例 `sketch_desk.png`
- 依赖：Python（`pip install pillow requests`）；出图脚本需本地 Stable Diffusion WebUI（A1111 / 绘世）保持运行、开启 API（`http://127.0.0.1:7860`），草图法另需对应 ControlNet 模型
- 用法：`python sd_gen.py examples/task_tile_desk.json --out 输出目录`；完整流程见 [sd-tools/style_guide.md](sd-tools/style_guide.md)

## folder_size.bat —— 文件夹大小排序器

把任意文件夹里的子文件夹按占用空间从大到小排出来，清理磁盘时先拿它找出「大头」（Windows）。

- 双击运行 = 统计本文件所在的文件夹；把目标文件夹拖到 .bat 上 = 统计它
- 实时显示扫描进度；权限不足、读不全的目录会在「备注」列标出来，不漏不瞒
- 用系统自带 robocopy 快速统计，异常时自动降级重扫，几十万文件的大目录也能扛
- 零依赖、免安装：Windows 10 / 11 自带组件直接运行，不需要 Python
- 建议右键「以管理员身份运行」，结果更完整（系统保护目录除外）
- 用法示例：复制到 `C:\Users\你的用户名` 下双击，一眼看清哪块最占地方

## 说明

仅供学习交流，转载请注明出处。
