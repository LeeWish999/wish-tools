# tile_pack.py v2 —— 拼 MV B-E 图块表 (16x16格, 768x768)
# 用法: python tile_pack.py 文件夹 --out 输出.png [--mode texture|object] [--quant 24] [--seam N]
# texture: 中心裁方 + Lanczos缩96 + 最近邻缩48 + 颜色量化(默认24色,去噪)
# object:  自动裁透明边 + 等比塞48居中留1px透明边（需先色键去底）
# --seam N: 额外导出前N块2x2无缝检查图
import sys, os, glob, argparse
from PIL import Image

TILE = 48
COLS, ROWS = 16, 16

def prep_texture(img, quant):
    w, h = img.size
    s = min(w, h)
    img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
    img = img.resize((TILE*2, TILE*2), Image.LANCZOS)
    img = img.resize((TILE, TILE), Image.NEAREST)
    if quant > 0:
        img = img.convert("RGB").quantize(colors=quant, method=Image.MEDIANCUT).convert("RGBA")
    return img

def prep_object(img):
    img = img.convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    scale = min(TILE / w, TILE / h)
    nw, nh = max(1, int(w*scale)-2), max(1, int(h*scale)-2)
    img = img.resize((nw, nh), Image.NEAREST)
    canvas = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    canvas.paste(img, ((TILE-nw)//2, (TILE-nh)//2), img)
    return canvas

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="tilesheet.png")
    ap.add_argument("--mode", choices=["texture", "object"], default="object")
    ap.add_argument("--quant", type=int, default=24, help="纹理模式色数量化(0=关闭)")
    ap.add_argument("--seam", type=int, default=0, help="导出前N块2x2无缝检查图")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.folder, "*.png")))
    if not files:
        print(f"[X] {args.folder} 里没有 PNG"); sys.exit(1)
    if len(files) > COLS*ROWS:
        files = files[:COLS*ROWS]

    if args.mode == "texture":
        prep = lambda im: prep_texture(im, args.quant)
    else:
        prep = prep_object

    sheet = Image.new("RGBA", (COLS*TILE, ROWS*TILE), (0, 0, 0, 0))
    for i, f in enumerate(files):
        tile = prep(Image.open(f).convert("RGBA"))
        sheet.paste(tile, ((i % COLS)*TILE, (i // COLS)*TILE), tile)
    sheet.save(args.out)
    prev = os.path.splitext(args.out)[0] + "_preview.png"
    sheet.resize((sheet.width*4, sheet.height*4), Image.NEAREST).save(prev)
    print(f"[OK] 图块表: {args.out} ({len(files)} 块) + 预览")

    if args.seam > 0:
        n = min(args.seam, len(files))
        for i in range(n):
            t = prep(Image.open(files[i]).convert("RGBA"))
            c = Image.new("RGBA", (TILE*2, TILE*2), (0, 0, 0, 0))
            for x in range(2):
                for y in range(2):
                    c.paste(t, (x*TILE, y*TILE), t)
            c.save(os.path.join(os.path.dirname(args.out), f"seam_{i+1}.png"))
        print(f"[OK] 无缝检查图: seam_1..seam_{n}.png")

if __name__ == "__main__":
    main()
