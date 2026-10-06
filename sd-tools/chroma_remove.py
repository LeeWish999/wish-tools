# chroma_remove.py v3 —— 边界泛洪 + 严格品红（保护皮肤/粉色，绝不啃洞）
# 1) 边缘采样背景色(中位数)  2) 仅从边界向内泛洪，连通才删 → 人物内部天然安全
# 3) 可选 --pockets：额外删除"被围住的大块背景"(如两腿间)，默认关闭
# 用法: python chroma_remove.py 帧文件夹 [--tol 70] [--pockets] [--min-area 300]
import sys, os, glob, argparse
from statistics import median
from collections import deque
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--tol", type=int, default=70, help="与采样背景色的曼哈顿距离容差")
    ap.add_argument("--pockets", action="store_true", help="额外删除被围住的大块背景区(默认关)")
    ap.add_argument("--min-area", type=int, default=300, help="pockets 最小面积px")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.folder, "*.png")))
    if not files:
        print(f"[X] {args.folder} 里没有 PNG"); sys.exit(1)

    for f in files:
        im = Image.open(f).convert("RGBA")
        w, h = im.size
        px = im.load()

        samples = []
        for x in range(w):
            for y in [0, 1, h-2, h-1]:
                if px[x, y][3] != 0:
                    samples.append(px[x, y][:3])
        for y in range(h):
            for x in [0, 1, w-2, w-1]:
                if px[x, y][3] != 0:
                    samples.append(px[x, y][:3])
        if not samples:
            print(f"[!] {os.path.basename(f)} 边缘全透明，跳过"); continue
        br = int(median(s[0] for s in samples))
        bg_ = int(median(s[1] for s in samples))
        bb = int(median(s[2] for s in samples))

        def is_bg(r, g, b):
            dist = abs(r-br) + abs(g-bg_) + abs(b-bb)
            if dist <= args.tol:
                return True
            # 严格品红：r/b都高、g明显低于两者、r≈b（皮肤/粉色不再误伤）
            return (r >= 120 and b >= 120 and g <= min(r, b) - 40 and abs(r - b) <= 50)

        removed = 0
        seen = set()
        q = deque()
        for x in range(w):
            for y in (0, h-1):
                if (x, y) not in seen and px[x, y][3] != 0:
                    seen.add((x, y)); q.append((x, y))
        for y in range(h):
            for x in (0, w-1):
                if (x, y) not in seen and px[x, y][3] != 0:
                    seen.add((x, y)); q.append((x, y))
        while q:
            x, y = q.popleft()
            r, g, b, a = px[x, y]
            if a != 0 and is_bg(r, g, b):
                px[x, y] = (0, 0, 0, 0); removed += 1
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                        seen.add((nx, ny)); q.append((nx, ny))

        pocket = 0
        if args.pockets:
            visited = set()
            for y in range(h):
                for x in range(w):
                    if px[x, y][3] == 0 or (x, y) in visited:
                        continue
                    r, g, b, a = px[x, y]
                    if not is_bg(r, g, b):
                        continue
                    comp = []
                    cq = deque([(x, y)]); visited.add((x, y))
                    while cq:
                        cx, cy = cq.popleft(); comp.append((cx, cy))
                        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                                rr, gg, bb, aa = px[nx, ny]
                                if aa != 0 and is_bg(rr, gg, bb):
                                    visited.add((nx, ny)); cq.append((nx, ny))
                    if len(comp) >= args.min_area:
                        for cx, cy in comp:
                            px[cx, cy] = (0, 0, 0, 0)
                        pocket += len(comp)

        im.save(f)
        print(f"去底: {os.path.basename(f)}  背景=({br},{bg_},{bb})  泛洪删{removed}px 口袋删{pocket}px")
    print("[OK] 完成")

if __name__ == "__main__":
    main()
