# -*- coding: utf-8 -*-
# img2pdf_worker.py —— 一个文件夹里的图片合成一个"图片型 PDF"
# 用法: python img2pdf_worker.py <图片文件夹>

import os, sys, glob

BASE     = os.path.dirname(os.path.abspath(__file__))                       # 脚本所在目录
OUT_ROOT = os.environ.get("OCR_OUT_ROOT") or os.path.join(BASE, "output")   # 输出总目录（可用环境变量覆盖）
OUT_DIR  = os.path.join(OUT_ROOT, "img-to-pdf")                             # 图片→PDF 输出

def log(*a):
    print(*a, flush=True)

def main():
    if len(sys.argv) < 2:
        log("[错误] 缺少图片文件夹参数"); sys.exit(1)
    folder = sys.argv[1]
    if not os.path.isdir(folder):
        log("[错误] 文件夹不存在:", folder); sys.exit(1)
    files = sorted(glob.glob(os.path.join(folder, "page_*.png")))
    if not files:
        files = [os.path.join(folder, f) for f in os.listdir(folder)
                 if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        files.sort()
    if not files:
        log("[错误] 该文件夹里没有图片"); sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)
    from PIL import Image
    imgs = []
    for f in files:
        im = Image.open(f).convert("RGB")
        imgs.append(im)
    name = os.path.basename(os.path.normpath(folder)) + "_图片型.pdf"
    out = os.path.join(OUT_DIR, name)
    imgs[0].save(out, save_all=True, append_images=imgs[1:], resolution=72.0)
    for im in imgs:
        im.close()
    log("[文件] " + out)
    log("[PDF] 已合成 %d 页 -> %s" % (len(imgs), name))
    log("[完成] " + out)

if __name__ == "__main__":
    main()
