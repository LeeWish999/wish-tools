# RPG Maker MV 像素素材风格库 v4（恐怖解密向）

> 配套本文件夹（sd-tools）的脚本集使用：记录底模 / LoRA 分工、提示词与参数基准、三大生产流程、质检体系与踩坑记录。

## 〇、最高优先级：三条铁律（任何流程不得违背）

1. **人工目测 = 第一验收标准。** 质检脚本与视觉模型只作参考——肉眼说不行，就是不行。
2. **去底核心原则：宁可少去，不可多去；不追求完美去底；保留尽可能多的原图细节。** 残留的背景块手动擦除，绝不为了"去干净"牺牲原图。
3. **本文件夹只放最终脚本与配置。** 测试产物一律放在仓库之外的独立工作目录，不向本文件夹写入任何生成图与日志。

## 一、尺寸规范

- **行走图 Character**：单角色 3列×4行 共12帧
  - 当前标准：每帧 **96×96**，整图 288×384（MV 原生支持，文件名加 `$` 前缀）
  - 旧标准：每帧 48×48（保留能力，一般不用）
- **脸图 Face**：144×144
- **图块 Tileset**：**48×48 每格**，整表 768×768（16×16 格）——图块永远是 48px，引擎写死
- **立绘 / 概念图**：512×768 起步
- 生成策略：先出大图（512 / 768），再最近邻缩放，保住像素颗粒

## 二、底模（Checkpoint）

- **主底模：anything-v5**（`sd1.5\anything-v5.safetensors`）——像素人物 / 物件 / 通用
- **恐怖底模：Ekmix-gen3**（`Ekmix-gen3.ckpt`）——恐怖场景 / 氛围
- **Illustrious XL**（`illustriousXLV01.C4Ut.safetensors`）——仅用于 RTP 风角色 / 立绘实验
- 已弃：NoobAI-XL-Vpred（A1111 上花屏，禁用）
- 切换：task.json 的 `override_settings.sd_model_checkpoint` 写文件名

## 三、LoRA 清单与分工（各自只干自己的活，严禁混用）

- **pixel sprites**（`pixel sprites.safetensors`）：人物帧 + 孤立物件（B-E 表）。触发词 `2d Pixel Art` / `sprite style` / `game character`，权重 0.7~0.8
- **16-bit pixel background**（`16-bit_pixel_background_SD1.5.safetensors`）：纹理 / 背景主力（A 类）。触发词 `apxlz`，权重 0.8，步数 50
- **basepixel**（`basepixel-20.safetensors`）：32px 粗粝风。已退出纹理主力（太糊），仅用于"故意做旧"效果，权重 0.6~1.0
- **PixelFusion**（`像素世界SD1.5PixelFusion_3D.safetensors`）：Minecraft 式 3D 像素，备用
- **mtilesetter**（`mtilesetter_lora_v2.safetensors`）：整表生成向，图块线已弃用。若再用，只许触发词 `minimalistic_tileset`，**永远禁用 `full_tileset`**（会画出满幅乱炖）
- **RPG_Maker**（`RPG_Maker.safetensors`）：Illustrious 底、官方素材训练的 RTP 风格。实测对图块物件透视无效（训练数据为角色插画）；仅保留给 RTP 风角色 / 立绘
- **SDXL 三件套**（已下载、未实验）：Animagine XL 底模 + Pixel Art Sprite Sheet LoRA；**2D Pixel Toolkit**（触发词 `PIXEL, PIXEL ART`）。开 SDXL 线时再启用

## 四、提示词基准

- 正向-像素基础：`pixel art, best quality, clean outline, 16-bit pixel art`
- 正向-人物 / 物件：`1girl/1boy, full body, front view`；孤立物件加 `single object, solid magenta background, flat color, no gradient`
- 正向-防裁切：`whole body visible, head to toe, centered, large character`
- 正向-恐怖氛围：`dark atmosphere, eerie, dim lighting, fog, abandoned school, old corridor, peeling wallpaper, muted colors, desaturated`
- 反向-全套（物件 / 人物必须携带）：
  `lowres, bad anatomy, blurry, watermark, text, signature, extra limbs, deformed, jpeg artifacts, low quality, worst quality, cropped, cut off, out of frame, partial body, head cut off, feet cut off, close-up, upper body, zoomed in, ring, circle, circular frame, halo, magic circle, emblem, badge, vignette, spotlight, isometric, perspective, 3/4 view, tilted, shadow, drop shadow, cast shadow, gradient background`

## 五、参数基准

- 步数 25~30（apxlz 纹理用 50）；CFG 5~7；采样器 `DPM++ 2M`
- 行走帧 / 物件：512 或 768 方图；纹理：512~768
- seed 规则：同一角色多帧固定一个 seed（如 888）；换角色换 seed；探索用 -1
- 96px 行走图用 768×768 生成 + `make_sheet --frame 96`

## 六、三大生产流程（已定案）

### A. 行走图（闭环验证过）

1. txt2img 生成 9 帧（下 / 左 / 上 × 站立 / 迈左 / 迈右），固定 seed，品红底
2. 右方向 3 帧 = 左方向 3 帧水平翻转（禁止生成，SD 分不清左右）
3. `chroma_remove.py` 保守去底（不带 `--pockets`）
4. `make_sheet.py --frame 96` 拼 3×4（288×384）
5. 文件名加 `$` 前缀拖入 MV；帧间风格漂移由人工目测验收

### B. 纹理（A 类：地板 / 墙）

1. 16-bit background LoRA + `tiling:true` + 满幅提示词生成（不要单件描述）
2. `tile_pack.py --mode texture --quant 24`（自动缩 48 + 量化）
3. 验收：seam 图看 2×2 拼接无缝；人工目测清晰度

### C. 物件（B-E 类：家具等）——抽卡 + 手修，不追求单张满分

1. 手绘草图：512×512、白底不透明、黑线 2~4px；结构只画必要线，顶面想多薄就画多薄（草图没画的地方模型会自由发挥）
2. `sd_cn.py` 草图法：`--model lineart_anime --weight 1.0`（ControlNet 锁结构）
3. 一次出 8 张（seed 1~8），人工目测挑 1~2 张合格的
4. `chroma_remove.py` 保守去底（默认无 `--pockets`；深红 / 紫红物件永远禁用 pockets，色相太近必啃洞）
5. 残留背景块用 Aseprite 手动擦（10 秒/件，接受不完美）
6. `tile_pack.py --mode object` 打包 + `tile_quant.py --colors 32` 量化
7. `tile_qa.py` + `tile_zoom.py` 数值复核 + 视觉模型参考意见（人工目测为最终判定）

## 七、质检体系（按权重排序）

1. **人工目测（第一标准）**
2. `tile_qa.py` 逐格体检（数值参考：残渣 / 品红残留 / 触边 / 色数）
3. `tile_zoom.py` 格子放大（目检辅助）
4. 视觉模型复核（参考意见，可对压缩预览判构图 / 透视 / 风格）
5. RTP 五条判据（物件）：无灭点无侧厚；顶面只许"边 / 口"级；零投影零光泽；单件纯色底可抠；低饱和平涂 + 细描边

## 八、脚本清单（本文件夹最终版）

| 脚本 | 用途 | 用法示例 |
| --- | --- | --- |
| `sd_gen.py` | 文生图（v2 防呆：重试 3 次 + 原子写） | `python sd_gen.py task.json --out 输出目录` |
| `sd_img2img.py` | 图生图（参考图锁定外观） | `python sd_img2img.py 参考图 --prompt "..." --seed X --denoise 0.6 --out 输出` |
| `sd_cn.py` | ControlNet 草图法（v3 已修 enabled；跑完自动存 .info.json，可验证是否生效） | `python sd_cn.py 草图.png --prompt "..." --model lineart_anime --out 输出` |
| `make_sheet.py` | 拼行走图 | `python make_sheet.py 帧文件夹 --out 输出.png --frame 96` |
| `chroma_remove.py` | 品红保守去底 | `python chroma_remove.py 文件夹`（默认无 pockets） |
| `remove_bg.py` | 四角泛洪去底（早期简化版，备用） | `python remove_bg.py 帧文件夹` |
| `fill_holes.py` | 去底后补小洞 | `python fill_holes.py 帧文件夹` |
| `tile_pack.py` | 拼图块表 | `--mode texture / object --quant N` |
| `tile_quant.py` | 限量色 | `--colors 32`（可选 `--global`） |
| `tile_qa.py` | 逐格体检 | `--out 报告.txt` |
| `tile_zoom.py` | 格子放大 | `格号列表 --scale 4` |

- 任务模板：`examples/` 下的 `task_walk.json`、`task_walk_hd.json`、`task_tile_floor.json`、`task_tile_desk.json`
- 参考草图：`examples/sketch_desk.png`（课桌范例）

## 九、文件夹规矩（不可违反）

- **sd-tools（本文件夹）**——只放最终脚本与配置；一切写入 / 删除手动执行，不自动写入。
- **工作目录**——测试中间产物（帧图、待处理件）放仓库之外的独立目录。
- **成品目录**——最终成品与原始生成图分开放；原图区只进不出（不覆盖原始图）。
- 跑任何输出脚本前：先关掉正开着输出文件的窗口（Errno 22 文件占用）。
- 生成前先备份原始帧到 `_raw` 子目录（去底是原地处理）。

## 十、环境备注

- 运行：系统 PATH 无 python 时，用本机解释器的完整路径调用脚本。
- 绘世需保持运行且「启用 API」开启（`http://127.0.0.1:7860`）。
- PowerShell 下跑脚本并捕获输出：`Start-Process -RedirectStandardOutput/-RedirectStandardError -Wait -PassThru`。
- 验证黄金标准：看输出文件是否存在 + 尺寸，而不是看命令打印。
- ControlNet 已装模型：scribble / lineart / lineart_anime / canny / softedge / mlsd / openpose / tile 等全量就绪。

## 十一、血泪教训（禁止重犯）

1. 花屏 / 黑图 = 底模与 LoRA 版本不匹配（SD1.5 LoRA 配 SDXL 底、vpred 底都会花屏）
2. ControlNet 单元必须写 `"enabled": true`，否则静默不生效（以 info.json 验证为准）
3. `full_tileset` 触发词会让模型画"整表乱炖"，单件物件永远不用
4. `chroma_remove` 的 `--pockets` 会啃深色物件内部（阴影色相近），默认关闭
5. 提示词里 `standing` 与 `walking` 同时出现 = 互相打架，腿不动
6. 去底脚本必须对"未处理的原始帧"跑，对已去底图二次处理会崩
