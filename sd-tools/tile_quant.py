# tile_quant.py —— 图块表限量色（无抖动；透明像素不进色板；alpha 原样保留）
# 用法:
#   python tile_quant.py 表.png --colors 32            逐格量化 → 表_q32.png
#   python tile_quant.py 表.png --colors 32 --global   全表共用一个色板 → 表_q32_g.png
#   python tile_quant.py 表.png --colors 32 --out 自定义.png
import argparse, os
from PIL import Image

try:
    QM, DN = Image.Quantize.MEDIANCUT, Image.Dither.NONE
except AttributeError:
    QM, DN = Image.MEDIANCUT, 0

def count_colors(im):
    return len({(r, g, b) for (r, g, b, a) in im.getdata() if a > 0})

def quant_rgba(im, colors):
    px = list(im.getdata())
    opaque = [(r, g, b) for (r, g, b, a) in px if a > 0]
    if not opaque:
        return im.copy()
    strip = Image.new("RGB", (len(opaque), 1))
    strip.putdata(opaque)
    strip = strip.quantize(colors=colors, method=QM, dither=DN)
    q = im.convert("RGB").quantize(palette=strip, dither=DN).convert("RGB")
    q.putalpha(im.getchannel("A"))
    return q

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--colors", type=int, default=32)
    ap.add_argument("--global", dest="global_q", action="store_true", help="全表共用一个色板")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tile", type=int, default=48)
    ap.add_argument("--cols", type=int, default=16)
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGBA")
    W, H = im.size
    rows = H // args.tile

    if args.global_q:
        out = quant_rgba(im, args.colors)
        label = f"全局 {args.colors} 色"
    else:
        out = im.copy()
        for r in range(rows):
            for c in range(args.cols):
                box = (c * args.tile, r * args.tile, (c + 1) * args.tile, (r + 1) * args.tile)
                cell = im.crop(box)
                if cell.getbbox() is None:
                    continue
                out.paste(quant_rgba(cell, args.colors), box)
        label = f"逐格 {args.colors} 色"

    if args.out is None:
        base, ext = os.path.splitext(args.image)
        args.out = f"{base}_q{args.colors}{'_g' if args.global_q else ''}{ext}"
    out.save(args.out)
    before, after = count_colors(im), count_colors(out)
    print(f"[OK] {args.out}")
    print(f"    色数: {before} → {after} ({label})")

if __name__ == "__main__":
    main()
