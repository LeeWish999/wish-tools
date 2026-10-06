# fill_holes.py —— 修复去底后衣服上的小洞
# 逻辑：完全封闭、面积 <= max_area 的透明块，用周围颜色自动填充；
# 接触图片边界的透明区(背景)与大面积区域(两腿间)保持透明
# 用法: python fill_holes.py 帧文件夹 [--max-area 200]
import sys, os, glob, argparse
from collections import deque
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--max-area", type=int, default=200, help="封闭透明块面积≤此值才填充")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.folder, "*.png")))
    if not files:
        print(f"[X] {args.folder} 里没有 PNG"); sys.exit(1)

    for f in files:
        im = Image.open(f).convert("RGBA")
        w, h = im.size
        px = im.load()

        visited = set()
        filled_total = 0
        for y in range(h):
            for x in range(w):
                if px[x, y][3] != 0 or (x, y) in visited:
                    continue
                comp = []
                touches_border = False
                q = deque([(x, y)]); visited.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    comp.append((cx, cy))
                    if cx == 0 or cy == 0 or cx == w-1 or cy == h-1:
                        touches_border = True
                    for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited \
                           and px[nx, ny][3] == 0:
                            visited.add((nx, ny)); q.append((nx, ny))
                if touches_border or len(comp) > args.max_area:
                    continue
                comp_set = set(comp)
                frontier = deque()
                for (cx, cy) in comp:
                    for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in comp_set \
                           and px[nx, ny][3] != 0:
                            frontier.append((cx, cy)); break
                done = set()
                while frontier:
                    cx, cy = frontier.popleft()
                    if (cx, cy) in done:
                        continue
                    done.add((cx, cy))
                    rs = gs = bs = n = 0
                    for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] != 0:
                            pr, pg, pb, _ = px[nx, ny]
                            rs += pr; gs += pg; bs += pb; n += 1
                    if n == 0:
                        continue
                    px[cx, cy] = (rs//n, gs//n, bs//n, 255)
                    filled_total += 1
                    for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                        if (nx, ny) in comp_set and (nx, ny) not in done:
                            frontier.append((nx, ny))
        im.save(f)
        print(f"补洞: {os.path.basename(f)} 填充 {filled_total}px")
    print("[OK] 完成")

if __name__ == "__main__":
    main()
