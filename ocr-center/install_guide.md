# ocr-center 从零安装教程

> 适用：Windows 10 / 11（64 位）。从没配过 Python 环境也能跟着做。
> 耗时：命令操作约 20~40 分钟，其余时间主要花在下载上。
> 最后更新：2026-10-06（文中版本号以官方文档当前说明为准）。

## 0. 这套工具是什么

「ocr-center」是一套书籍数字化小工具集，共 7 个文件：

| 文件 | 作用 |
| --- | --- |
| `ocr_center.pyw` | 「OCR 中心」图形界面：① PDF→图片 ② 图片→PDF ③ OCR→Markdown ④ 全自动流水线（单个 / 批量） |
| `pdf2png_worker.py` | PDF 逐页转 PNG（被中心 / bat 调用，也可独立命令行运行） |
| `img2pdf_worker.py` | 一批图片合成「图片型 PDF」 |
| `ocr_worker.py` | 调用 PaddleOCR-VL 做 OCR，逐页输出 Markdown / JSON / Word |
| `pdf_to_png.bat`、`img_to_pdf.bat`、`ocr_latex.bat` | 命令行菜单入口（不想开图形界面时用） |

所有输出默认落在本文件夹的 `output\` 下：`pdf-to-png` / `img-to-pdf` / `ocr` 三个子文件夹。

## 1. 准备工作

- **系统**：Windows 10 / 11（64 位）
- **显卡**：推荐 NVIDIA 独立显卡；纯 CPU 也能跑，但速度会慢很多
- **显卡驱动**：更新到较新版本（使用 CUDA 12.6 版安装包时，驱动需 ≥ 550.54.14）
- **磁盘空间**：建议预留 10 GB 以上（环境 + 模型文件）
- **网络**：安装依赖、首次运行下载模型都需要联网

## 2. 安装 Python

1. 打开 <https://www.python.org/downloads/> ，下载 **Python 3.11 或 3.12**（64 位）。PaddleX 支持 Python 3.8 ~ 3.13，别选超出范围的版本。
2. 安装时勾选 **Add python.exe to PATH**，其余默认即可（建议用官网安装包）。
3. 验证：按 `Win+R` 输入 `cmd` 回车，运行：

```bat
python --version
```

能打印出版本号即可。

## 3. 下载工具文件

1. 打开本仓库（wish-tools）页面，把 `ocr-center` 文件夹整体下载（Code → Download ZIP 后解压，或逐个下载 7 个文件）。
2. 放到一个**简短的英文路径**下，例如 `C:\ocr-center`（避免中文和空格，少踩坑）。
3. 对照第 0 节的表格，确认 7 个文件都在。
4. 如果文件是从网上下载的压缩包解出来的，双击 `.bat` / `.pyw` 没反应时：右键文件 → 属性 → 勾选「解除锁定」。

## 4. 创建虚拟环境（推荐）

打开 cmd，依次运行：

```bat
cd /d C:\ocr-center
python -m venv .venv
```

工具会自动识别本目录下的 `.venv`，不需要额外配置。

> 之后所有命令都用 `.venv\Scripts\python.exe` 来执行；也可以先运行 `.venv\Scripts\activate` 激活后直接用 `pip` / `python`（下同）。

## 5. 安装基础依赖

```bat
.venv\Scripts\python.exe -m pip install pypdfium2 pillow python-docx
```

（下载慢可加国内镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`）

这三个包分别负责：PDF 渲染、图片处理、Word 输出。

## 6. 安装 OCR 引擎（PaddlePaddle + PaddleX）

OCR 功能由飞桨（PaddlePaddle）和 PaddleX 驱动，分两步。

### 6.1 安装 PaddlePaddle

**GPU 版（推荐）** —— 先确认显卡驱动 ≥ 550.54.14：

```bat
.venv\Scripts\python.exe -m pip install paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
```

驱动较旧（≥ 452.39）的话，改用 CUDA 11.8 的包（把地址换成 `https://www.paddlepaddle.org.cn/packages/stable/cu118/`）。

**CPU 版（没有独显 / 先跑通流程）**：

```bat
.venv\Scripts\python.exe -m pip install paddlepaddle==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

> 注意：
> - 不用管系统里装没装 CUDA，**只看显卡驱动版本**（官方说明）。
> - **NVIDIA 50 系显卡（Windows）**：常规包无法直接支持，请按官方安装文档「Windows 系统适配 NVIDIA 50 系显卡」一节选择对应 wheel。
> - 命令里的 `3.3.0` 是官方文档当前版本；日后如提示版本不存在，去掉 `==3.3.0` 或到官方安装页选最新命令。

### 6.2 安装 PaddleX

```bat
.venv\Scripts\python.exe -m pip install "paddlex[ocr]"
```

### 6.3 验证

```bat
.venv\Scripts\python.exe -c "import paddle; print('paddle', paddle.__version__)"
.venv\Scripts\python.exe -c "import paddle; print(paddle.device.get_device())"
.venv\Scripts\python.exe -c "import paddlex, pypdfium2, PIL, docx; print('all deps OK')"
```

分别打印出版本号、运行设备（如 `gpu:0` / `cpu`）、`all deps OK` 即成功。

## 7. 让工具找到你的环境（可选）

默认情况下**不需要任何配置**。工具按这个顺序找 Python：

1. 环境变量 `OCR_PYTHON`（如果有设置）
2. 本文件夹下的 `.venv` / `venv` 虚拟环境（第 4 步就是为了这个）
3. 系统 PATH 里的 Python

如果你的环境建在别处（如 `C:\envs\ocr`），设置一次即可：

```bat
setx OCR_PYTHON "C:\envs\ocr\Scripts\python.exe"
```

（重开程序后生效；重新 `setx` 可改。）

**更换输出位置**（可选）：默认输出在本文件夹 `output\`；想放别处：

```bat
setx OCR_OUT_ROOT "D:\ocr-output"
```

之后输出会落在 `D:\ocr-output\pdf-to-png` 等三个子文件夹。

## 8. 首次运行与验证

1. 双击 `ocr_center.pyw`，出现「OCR 中心」窗口。
2. 看日志第一行：应为 `[信息] worker 解释器：...`，路径指向你刚配好的环境。不对的话回到第 7 节。
3. 先用 ①（PDF→图片）跑个小文件，验证基础环境；再试 ③ OCR。
4. **首次 OCR 会先自动下载模型**（需要联网，等待较久，日志会停在「正在加载版面检测 + OCR 大模型」属正常），完成后每页滚动一行 `第 N/xx 页完成`。
5. 结果在 `output\ocr\<文件名>_<时间戳>\`：每页 `.md` / `.json` / `.docx` 三件套，加 `全书合并.md` / `.json` / `.docx` 三个合并文件。

> 跑 OCR 前尽量关掉其它占用显卡的程序（游戏、其它 OCR / AI 工具等），避免显存不足。

### 安装完成自检（清单）

- [ ] `python --version` 有输出
- [ ] 工具目录下有 `.venv`
- [ ] 三个基础包已安装（第 5 节命令无报错）
- [ ] `import paddle` 验证通过
- [ ] `import paddlex` 验证通过
- [ ] 双击 `ocr_center.pyw` 能开窗，日志首行指向正确解释器
- [ ] 小 PDF 跑通 ① 和 ③

## 9. 日常使用

三种用法，挑习惯的用：

- **图形界面**：双击 `ocr_center.pyw`。四个功能都支持单个 / 批量；跑完会有弹窗询问是否删除中间数据（不影响最终 OCR 结果）；「固定到开始菜单」按钮可创建快捷方式。
- **命令行菜单**：双击三个 `.bat` 之一，同样支持单个 / 批量。
- **命令行直接跑**：`.venv\Scripts\python.exe ocr_worker.py <pdf路径>`（其余两个脚本同理，参数见各文件头注释）。

小提示：批量处理时，同一批任务只加载一次模型，比一个个单独跑快得多。

## 10. 常见问题

| 现象 | 处理 |
| --- | --- |
| 双击 `.pyw` 没反应 | 右键 → 打开方式 → 选择 `pythonw.exe`；或先在 cmd 里运行 `.venv\Scripts\python.exe ocr_center.pyw`（要用 python.exe 才会显示报错信息） |
| 日志提示 `[错误] 未找到可用的 python.exe` | 回到第 7 节：把 `.venv` 建在工具文件夹里，或设置 `OCR_PYTHON` |
| 日志提示 `缺少脚本` | 7 个文件没放全，对照第 0 节表格 |
| `import paddlex` 报错 / 找不到模块 | PaddleX 没装进 `.venv`：`.venv\Scripts\python.exe -m pip install "paddlex[ocr]"` 重装 |
| 启动时卡几秒才弹窗口 | 正常：paddlex 导入时会先测试模型平台连通性（官方行为）。官方 FAQ 说明，确定只用本地模型时可设 `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=1` 跳过该检查 |
| 首次 OCR 很久没动静 | 在下载模型（看任务管理器网络占用）；模型也可能来自 Hugging Face / AI Studio / ModelScope 之一，视网络而定 |
| 报 CUDA / 驱动相关错误 | 更新显卡驱动；或改装 cu118 版；50 系显卡见 6.1 注释 |
| 显存不足（out of memory） | 关掉其它占显存的程序；先拿小 PDF 试 |
| 速度慢 | CPU 模式本来就慢；GPU 模式可在任务管理器里确认显卡是否在干活 |
| 中途关掉了，进度会不会丢 | 不会全丢：工具逐页写盘，已完成的页面文件保留在输出文件夹里；重跑会生成新的时间戳文件夹 |
| `.bat` 打开中文乱码 | 如编辑过，另存为 ANSI 编码；未编辑仍乱码可反馈 |
| 想提高图片清晰度 | 改 `pdf2png_worker.py` 里的 `DPI = 200`（150~300 之间） |
| pip 下载慢 / 失败 | 加国内镜像重试；PaddlePaddle 请务必使用命令里自带的 `-i` 地址 |

## 11. 卸载

- 删除整个文件夹即可（虚拟环境、输出都在里面；若设过 `OCR_OUT_ROOT` 指向别处，一并删除即可）。
- 设过的环境变量（`OCR_PYTHON` / `OCR_OUT_ROOT`）：在「设置 → 系统 → 系统信息 → 高级系统设置 → 环境变量」里删除。
- 模型文件由 PaddleX 缓存在用户目录中，需要彻底清理时可参考官方文档查询缓存位置后手动删除。

## 12. 参考（官方文档）

- PaddleX 文档总入口：<https://paddlepaddle.github.io/PaddleX/>
- 安装 PaddlePaddle：<https://paddlepaddle.github.io/PaddleX/latest/installation/paddlepaddle_install.html>
- 安装 PaddleX：<https://paddlepaddle.github.io/PaddleX/latest/installation/installation.html>
- PaddleOCR-VL 产线：<https://paddlepaddle.github.io/PaddleX/latest/pipeline_usage/tutorials/ocr_pipelines/PaddleOCR-VL.html>
- 常见问题 FAQ：<https://paddlepaddle.github.io/PaddleX/latest/FAQ.html>
- 飞桨安装命令选择器：<https://www.paddlepaddle.org.cn/install/quick>
