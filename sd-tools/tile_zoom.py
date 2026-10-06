# tile_zoom.py —— 指定格子放大目检（最近邻不插值），可贴2x2看接缝
# 用法:
#   python tile_zoom.py 表.png 1,13,15 --scale 4          # 从整表按格子号(左上=1,按行)取
#   python tile_zoom.py 表.png 1,13 --scale 4 --wrap      # 额外输出该格2x2平铺图(查接缝)
#   python tile_zoom.py 单张.png --scale 4                # 格号留空 = 整张放大(单图用)
#   ※ 默认 48px 格、16 列；不是768表就加 --tile/--cols
import sys, os, argparse
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("cells", nargs="*", default=[])
    ap.add_argument("--tile", type=int, default=48)
    ap.add_argument("--cols", type=int, default=16)
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--wrap", action="store_true")
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGBA")
    base = os.path.splitext(os.path.basename(args.image))[0]

    def zoom(t, tag):
        z = t.resize((t.width * args.scale, t.height * args.scale), Image.NEAREST)
        out = f"zoom_{base}_{tag}.png"
        z.save(out)
        print("[i]", out, f"{z.width}x{z.height}")

    ids = [int(v) for c in args.cells for v in c.split(",") if v.strip().isdigit()]
    if not ids:
        zoom(im, "all")
    else:
        for i in ids:
            r, c = (i - 1) // args.cols, (i - 1) % args.cols
            box = (c * args.tile, r * args.tile, c * args.tile + args.tile, r * args.tile + args.tile)
            t = im.crop(box)
            zoom(t, str(i))
            if args.wrap:
                p2 = Image.new("RGBA", (args.tile * 2, args.tile * 2))
                for ox, oy in ((0, 0), (args.tile, 0), (0, args.tile), (args.tile, args.tile)):
                    p2.paste(t, (ox, oy))
                zoom(p2, f"{i}_wrap")
    print("[i] 完成。把 zoom_*.png 发我，我逐个定论。")

if __name__ == "__main__":
    main()
