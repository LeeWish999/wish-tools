# remove_bg.py v1 —— 四角泛洪安全去底（人物永不误删，代价：围住的小区域可能残留）
# 用法: python remove_bg.py 帧文件夹 [--tol 45]
# 必须对未去底的原始帧运行（对已去底的图二次处理会出错）
import sys, os, glob, argparse
from collections import deque
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--tol", type=int, default=45, help="背景色容差，默认45")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.folder, "*.png")))
    if not files:
        print(f"[X] {args.folder} 里没有 PNG"); sys.exit(1)

    for f in files:
        im = Image.open(f).convert("RGBA")
        w, h = im.size
        px = im.load()
        corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
        bg = None
        for x, y in corners:
            if px[x, y][3] != 0:
                bg = px[x, y]
                break
        if bg is None:
            print(f"[!] {os.path.basename(f)} 四角已透明，需对原始帧运行"); sys.exit(1)

        seen = set(); q = deque()
        for c in corners:
            q.append(c); seen.add(c)
        while q:
            x, y = q.popleft()
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if abs(r-bg[0]) <= args.tol and abs(g-bg[1]) <= args.tol and abs(b-bg[2]) <= args.tol:
                px[x, y] = (0, 0, 0, 0)
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                        seen.add((nx, ny)); q.append((nx, ny))
        im.save(f)
        print(f"去底: {os.path.basename(f)}")
    print("[OK] 完成")

if __name__ == "__main__":
    main()
