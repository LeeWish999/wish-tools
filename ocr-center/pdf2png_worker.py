# -*- coding: utf-8 -*-
# pdf2png_worker.py —— 单个 PDF 渲染为 PNG（供 OCR 中心 调用）
# 用法: python pdf2png_worker.py <pdf路径>

import os, sys, datetime

DPI = 200  # 渲染分辨率，150~300 都行，想改就改这里

BASE     = os.path.dirname(os.path.abspath(__file__))                       # 脚本所在目录
OUT_ROOT = os.environ.get("OCR_OUT_ROOT") or os.path.join(BASE, "output")   # 输出总目录（可用环境变量覆盖）
OUT_DIR  = os.path.join(OUT_ROOT, "pdf-to-png")                             # PDF→图片 输出

def log(*a):
    print(*a, flush=True)

def main():
    if len(sys.argv) < 2:
        log("[错误] 缺少 PDF 路径参数"); sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.isfile(pdf_path):
        log("[错误] 文件不存在:", pdf_path); sys.exit(1)
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf_path)
    n = len(doc)
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(OUT_DIR, "%s_%s" % (stem, ts))
    os.makedirs(out_dir, exist_ok=True)
    log("[目录] " + out_dir)
    log("[图片] %s 共 %d 页，开始渲染…" % (os.path.basename(pdf_path), n))
    scale = DPI / 72.0
    for i in range(n):
        page = doc[i]
        bmp = page.render(scale=scale)
        pil = bmp.to_pil()
        pil.save(os.path.join(out_dir, "page_%04d.png" % (i + 1)))
        if (i + 1) % 10 == 0 or (i + 1) == n:
            log("[图片] 已渲染 %d/%d 页" % (i + 1, n))
    doc.close()
    log("[完成] " + out_dir)

if __name__ == "__main__":
    main()
