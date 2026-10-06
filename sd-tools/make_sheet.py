# make_sheet.py v4 —— 单帧拼 RPG Maker MV 行走图 + 4x预览图
# 用法:
#   python make_sheet.py 帧文件夹 --out 输出.png [--repeat-rows] [--pre] [--frame 48|96]
# --frame: 每帧格子边长(px)，默认48；96=大精灵(整图288×384)
import os, sys, argparse, glob
from PIL import Image

def fit_square(img, frame, pre=False):
    if pre:
        mid = frame * 2
        s = mid / max(img.size)
        img = img.resize((max(1, int(img.width*s)), max(1, int(img.height*s))), Image.LANCZOS)
    s = frame / max(img.size)
    nw, nh = max(1, int(img.width*s)), max(1, int(img.height*s))
    img = img.resize((nw, nh), Image.NEAREST)
    canvas = Image.new("RGBA", (frame, frame), (0, 0, 0, 0))
    canvas.paste(img, ((frame-nw)//2, (frame-nh)//2), img)
    return canvas

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="sheet.png")
    ap.add_argument("--repeat-rows", action="store_true")
    ap.add_argument("--pre", action="store_true", help="先Lanczos缩到2x再最近邻到目标格")
    ap.add_argument("--frame", type=int, default=48, help="每帧格子边长(px)，48或96")
    args = ap.parse_args()

    frame = args.frame
    files = sorted(glob.glob(os.path.join(args.folder, "*.png")))
    if not files:
        print(f"[X] {args.folder} 里没有 PNG"); sys.exit(1)
    cells = [fit_square(Image.open(f).convert("RGBA"), frame, args.pre) for f in files]
    print(f"读取 {len(cells)} 帧, 格子={frame}px")

    n = len(cells)
    if n >= 12:
        rows = [cells[r*3:(r+1)*3] for r in range(4)]
    elif n % 3 == 0:
        rows = [cells[0:3] for _ in range(4)] if args.repeat_rows else \
               [cells[r*3:(r+1)*3] for r in range(n//3)]
    else:
        print("[X] 帧数需为3的倍数"); sys.exit(1)

    sheet = Image.new("RGBA", (frame*3, frame*4), (0, 0, 0, 0))
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            sheet.paste(cell, (c*frame, r*frame), cell)
    sheet.save(args.out)

    prev = os.path.splitext(args.out)[0] + "_preview.png"
    sheet.resize((sheet.width*4, sheet.height*4), Image.NEAREST).save(prev)
    print(f"[OK] 行走图: {args.out} ({frame*3}x{frame*4})")
    print(f"[OK] 预览图: {prev}")
    print("提示: MV 单角色文件名加 $ 前缀；96px 时用 $hero.png 直接拖入引擎即 96 精灵")

if __name__ == "__main__":
    main()
