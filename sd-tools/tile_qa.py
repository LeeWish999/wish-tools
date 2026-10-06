# tile_qa.py —— 图块表逐格体检（接缝/裁切/残渣/风格/贴边/无缝性）
# 用法:
#   python tile_qa.py B表.png
#   python tile_qa.py B表.png --wrap 1,2,3,4        # 这里填“要求无缝”的纹理格号: 出2x2目检图+边界连续性数值
#   python tile_qa.py B表.png --out 报告.txt --tile 48 --semi-min 1 --seam-ratio 3.0
# 产物:
#   ① 按格编号清单(控制台 + --out 文件)  ② <表>_qa.png 问题格红框总览  ③ <表>_wrap_N.png 2x2无缝目检
import sys, os, math, argparse
from statistics import median
from PIL import Image, ImageDraw

def d3(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

def check_sheet(sheet, tile=48, wrap_ids=(), semi_min=1, mag_gap=50, seam_ratio=3.0):
    im = Image.open(sheet).convert("RGBA")
    W, H = im.size
    cols, rows = W // tile, H // tile
    total = cols * rows
    px = im.load()
    hp = im.convert("RGB").convert("HSV").load()
    problems, styles, notes = {}, {}, []
    for idx in range(1, total + 1):
        r, c = (idx - 1) // cols, (idx - 1) % cols
        x0, y0 = c * tile, r * tile
        semi = mag = opaque = 0
        touch = {"上": 0, "下": 0, "左": 0, "右": 0}
        hx = hy = ss = vv = 0.0
        colors = set()
        for y in range(y0, y0 + tile):
            for x in range(x0, x0 + tile):
                R, G, B, A = px[x, y]
                if A == 0:
                    continue
                opaque += 1
                if A < 255:
                    semi += 1
                if R > 160 and B > 160 and (min(R, B) - G) > mag_gap:
                    mag += 1
                colors.add((R, G, B))
                hh, s2, v2 = hp[x, y]
                ang = hh * (2 * math.pi / 255.0)
                hx += math.cos(ang)
                hy += math.sin(ang)
                ss += s2
                vv += v2
                if y == y0:
                    touch["上"] += 1
                if y == y0 + tile - 1:
                    touch["下"] += 1
                if x == x0:
                    touch["左"] += 1
                if x == x0 + tile - 1:
                    touch["右"] += 1
        if opaque == 0:
            continue
        hue = math.degrees(math.atan2(hy, hx)) % 360 if (abs(hx) + abs(hy)) > 1e-9 else 0.0
        styles[idx] = (hue, ss / opaque / 255.0, vv / opaque / 255.0, len(colors))
        issues = []
        if semi >= semi_min:
            issues.append(f"半透明残渣{semi}px")
        if mag > 0:
            issues.append(f"品红残留{mag}px")
        if opaque < tile * tile:
            hits = [f"{k}{v}px" for k, v in touch.items() if v > 0]
            if hits:
                issues.append("内容触边(" + ",".join(hits) + ")")
        if issues:
            problems[idx] = issues
    for idx in sorted(set(wrap_ids)):
        if not (1 <= idx <= total):
            notes.append(f"[!] --wrap 第{idx}格超范围,跳过")
            continue
        r, c = (idx - 1) // cols, (idx - 1) % cols
        t_im = im.crop((c * tile, r * tile, c * tile + tile, r * tile + tile))
        tp = t_im.load()
        de = sum(d3(tp[tile - 1, y], tp[0, y]) for y in range(tile)) / tile
        base = median([sum(d3(tp[x, y], tp[x + 1, y]) for y in range(tile)) / tile for x in range(tile - 1)])
        dv = sum(d3(tp[x, tile - 1], tp[x, 0]) for x in range(tile)) / tile
        basev = median([sum(d3(tp[x, y], tp[x, y + 1]) for y in range(tile - 1)) / (tile - 1) for x in range(tile)])
        rh = de / max(1e-6, base)
        rv = dv / max(1e-6, basev)
        tag = ""
        if max(rh, rv) > seam_ratio:
            tag = "  ← 可疑不连续"
            problems.setdefault(idx, []).append(f"边界不连续(横{rh:.1f}x/纵{rv:.1f}x)")
        notes.append(f"[无缝] 第{idx}格: 左右 {de:.1f}(内部基准 {base:.1f}, {rh:.2f}x) | 上下 {dv:.1f}(基准 {basev:.1f}, {rv:.2f}x){tag}")
        p2 = Image.new("RGBA", (tile * 2, tile * 2))
        for ox, oy in ((0, 0), (tile, 0), (0, tile), (tile, tile)):
            p2.paste(t_im, (ox, oy))
        p2.save(f"{os.path.splitext(sheet)[0]}_wrap_{idx}.png")
    ann = im.copy()
    dr = ImageDraw.Draw(ann)
    for idx in problems:
        r, c = (idx - 1) // cols, (idx - 1) % cols
        dr.rectangle([c * tile, r * tile, c * tile + tile - 1, r * tile + tile - 1], outline=(255, 0, 0), width=2)
    ann.save(f"{os.path.splitext(sheet)[0]}_qa.png")
    rep = []
    rep.append(f"[i] {os.path.basename(sheet)} {W}x{H}, 网格 {cols}x{rows}={total}, 非空 {len(styles)} 格")
    rep.append(f"[i] 判据: 残渣=0<alpha<255; 品红=R>160 且 B>160 且 min(R,B)-G>{mag_gap}; 触边=含透明格内容碰格边; 无缝=边界差/内部差>{seam_ratio}")
    rep.append("[i] 非空格: " + ",".join(str(i) for i in sorted(styles)))
    for idx in sorted(styles):
        rep.append(f"第{idx}格: " + ("；".join(problems[idx]) if idx in problems else "通过"))
    if notes:
        rep.append("")
        rep.extend(notes)
    rep.append("")
    rep.append("[风格] 非空格 H(色相°) S(饱和) V(明度) 色数:")
    for idx in sorted(styles):
        h, s, v, n = styles[idx]
        rep.append(f"  第{idx}格: H{h:6.1f}  S{s:.2f}  V{v:.2f}  色数{n}")
    if len(styles) > 1:
        ms, mv = median([styles[i][1] for i in styles]), median([styles[i][2] for i in styles])
        out_s = [f"第{i}格" for i in styles if abs(styles[i][1] - ms) > 0.35]
        out_v = [f"第{i}格" for i in styles if abs(styles[i][2] - mv) > 0.35]
        if out_s:
            rep.append("[!] 饱和度离群: " + "、".join(out_s))
        if out_v:
            rep.append("[!] 明度离群: " + "、".join(out_v))
    if problems:
        rep.append("[!] 问题格: " + "、".join(f"第{i}格" for i in sorted(problems)))
    else:
        rep.append("[OK] 逐格检查全部通过")
    text = "\n".join(rep)
    print(text)
    return text, problems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet", help="图块表 PNG 路径")
    ap.add_argument("--tile", type=int, default=48)
    ap.add_argument("--wrap", type=str, default="", help="逗号分隔的格号(要求无缝的纹理格)")
    ap.add_argument("--out", type=str, default="")
    ap.add_argument("--semi-min", type=int, default=1)
    ap.add_argument("--mag-gap", type=int, default=50)
    ap.add_argument("--seam-ratio", type=float, default=3.0)
    args = ap.parse_args()
    if not os.path.isfile(args.sheet):
        print(f"[X] 找不到: {args.sheet}")
        sys.exit(1)
    wrap_ids = [int(s) for s in args.wrap.split(",") if s.strip().isdigit()] if args.wrap else []
    text, _ = check_sheet(args.sheet, args.tile, wrap_ids, args.semi_min, args.mag_gap, args.seam_ratio)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[i] 报告已写入: {args.out}")

if __name__ == "__main__":
    main()
