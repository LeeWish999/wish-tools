#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A3 Periodic Table of the Elements (English + 中文名称 + 电子排布) -- generator
================================================================================
生成可打印的 A3 (420 x 297 mm, 横向) 元素周期表。

每个格子内容：左上角原子序数 | 右上角中文名 | 元素符号 | 英文全名
              | 电子排布（惰性气体原子实缩写） | 相对原子质量
另有：族号 1-18、周期号 1-7、s/d/p/f 区标注、按族着色图例、镧系/锕系两行。

依赖:   pip install matplotlib
用法:   python periodic_table.py  ->  在脚本同目录生成 periodic_table_A3.pdf / .png
字体:   自动扫描系统字体并逐字选择（无需配置）；若个别新造字缺字形，
        下载 Noto Sans CJK SC 后把字体文件改名为 cjk.ttf 放到本脚本同目录即可。
打印:   用 PDF；A3 横向、缩放 100%（实际大小）、彩色。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import ft2font
from matplotlib.patches import Rectangle

# ---------- 元素数据 (原子序数, 符号, 英文名, 相对原子质量, 分类) ----------
ELEMENTS = [
    (1, "H", "Hydrogen", "1.008", "nonmetal"), (2, "He", "Helium", "4.0026", "noble"),
    (3, "Li", "Lithium", "6.94", "alkali"), (4, "Be", "Beryllium", "9.0122", "alkaline"),
    (5, "B", "Boron", "10.81", "metalloid"), (6, "C", "Carbon", "12.011", "nonmetal"),
    (7, "N", "Nitrogen", "14.007", "nonmetal"), (8, "O", "Oxygen", "15.999", "nonmetal"),
    (9, "F", "Fluorine", "18.998", "halogen"), (10, "Ne", "Neon", "20.180", "noble"),
    (11, "Na", "Sodium", "22.990", "alkali"), (12, "Mg", "Magnesium", "24.305", "alkaline"),
    (13, "Al", "Aluminium", "26.982", "post_transition"), (14, "Si", "Silicon", "28.085", "metalloid"),
    (15, "P", "Phosphorus", "30.974", "nonmetal"), (16, "S", "Sulfur", "32.06", "nonmetal"),
    (17, "Cl", "Chlorine", "35.45", "halogen"), (18, "Ar", "Argon", "39.95", "noble"),
    (19, "K", "Potassium", "39.098", "alkali"), (20, "Ca", "Calcium", "40.078", "alkaline"),
    (21, "Sc", "Scandium", "44.956", "transition"), (22, "Ti", "Titanium", "47.867", "transition"),
    (23, "V", "Vanadium", "50.942", "transition"), (24, "Cr", "Chromium", "51.996", "transition"),
    (25, "Mn", "Manganese", "54.938", "transition"), (26, "Fe", "Iron", "55.845", "transition"),
    (27, "Co", "Cobalt", "58.933", "transition"), (28, "Ni", "Nickel", "58.693", "transition"),
    (29, "Cu", "Copper", "63.546", "transition"), (30, "Zn", "Zinc", "65.38", "transition"),
    (31, "Ga", "Gallium", "69.723", "post_transition"), (32, "Ge", "Germanium", "72.630", "metalloid"),
    (33, "As", "Arsenic", "74.922", "metalloid"), (34, "Se", "Selenium", "78.971", "nonmetal"),
    (35, "Br", "Bromine", "79.904", "halogen"), (36, "Kr", "Krypton", "83.798", "noble"),
    (37, "Rb", "Rubidium", "85.468", "alkali"), (38, "Sr", "Strontium", "87.62", "alkaline"),
    (39, "Y", "Yttrium", "88.906", "transition"), (40, "Zr", "Zirconium", "91.222", "transition"),
    (41, "Nb", "Niobium", "92.906", "transition"), (42, "Mo", "Molybdenum", "95.95", "transition"),
    (43, "Tc", "Technetium", "[97]", "transition"), (44, "Ru", "Ruthenium", "101.07", "transition"),
    (45, "Rh", "Rhodium", "102.91", "transition"), (46, "Pd", "Palladium", "106.42", "transition"),
    (47, "Ag", "Silver", "107.87", "transition"), (48, "Cd", "Cadmium", "112.41", "transition"),
    (49, "In", "Indium", "114.82", "post_transition"), (50, "Sn", "Tin", "118.71", "post_transition"),
    (51, "Sb", "Antimony", "121.76", "metalloid"), (52, "Te", "Tellurium", "127.60", "metalloid"),
    (53, "I", "Iodine", "126.90", "halogen"), (54, "Xe", "Xenon", "131.29", "noble"),
    (55, "Cs", "Caesium", "132.91", "alkali"), (56, "Ba", "Barium", "137.33", "alkaline"),
    (57, "La", "Lanthanum", "138.91", "lanthanide"), (58, "Ce", "Cerium", "140.12", "lanthanide"),
    (59, "Pr", "Praseodymium", "140.91", "lanthanide"), (60, "Nd", "Neodymium", "144.24", "lanthanide"),
    (61, "Pm", "Promethium", "[145]", "lanthanide"), (62, "Sm", "Samarium", "150.36", "lanthanide"),
    (63, "Eu", "Europium", "151.96", "lanthanide"), (64, "Gd", "Gadolinium", "157.25", "lanthanide"),
    (65, "Tb", "Terbium", "158.93", "lanthanide"), (66, "Dy", "Dysprosium", "162.50", "lanthanide"),
    (67, "Ho", "Holmium", "164.93", "lanthanide"), (68, "Er", "Erbium", "167.26", "lanthanide"),
    (69, "Tm", "Thulium", "168.93", "lanthanide"), (70, "Yb", "Ytterbium", "173.05", "lanthanide"),
    (71, "Lu", "Lutetium", "174.97", "lanthanide"), (72, "Hf", "Hafnium", "178.49", "transition"),
    (73, "Ta", "Tantalum", "180.95", "transition"), (74, "W", "Tungsten", "183.84", "transition"),
    (75, "Re", "Rhenium", "186.21", "transition"), (76, "Os", "Osmium", "190.23", "transition"),
    (77, "Ir", "Iridium", "192.22", "transition"), (78, "Pt", "Platinum", "195.08", "transition"),
    (79, "Au", "Gold", "196.97", "transition"), (80, "Hg", "Mercury", "200.59", "transition"),
    (81, "Tl", "Thallium", "204.38", "post_transition"), (82, "Pb", "Lead", "207.2", "post_transition"),
    (83, "Bi", "Bismuth", "208.98", "post_transition"), (84, "Po", "Polonium", "[209]", "post_transition"),
    (85, "At", "Astatine", "[210]", "halogen"), (86, "Rn", "Radon", "[222]", "noble"),
    (87, "Fr", "Francium", "[223]", "alkali"), (88, "Ra", "Radium", "[226]", "alkaline"),
    (89, "Ac", "Actinium", "[227]", "actinide"), (90, "Th", "Thorium", "232.04", "actinide"),
    (91, "Pa", "Protactinium", "231.04", "actinide"), (92, "U", "Uranium", "238.03", "actinide"),
    (93, "Np", "Neptunium", "[237]", "actinide"), (94, "Pu", "Plutonium", "[244]", "actinide"),
    (95, "Am", "Americium", "[243]", "actinide"), (96, "Cm", "Curium", "[247]", "actinide"),
    (97, "Bk", "Berkelium", "[247]", "actinide"), (98, "Cf", "Californium", "[251]", "actinide"),
    (99, "Es", "Einsteinium", "[252]", "actinide"), (100, "Fm", "Fermium", "[257]", "actinide"),
    (101, "Md", "Mendelevium", "[258]", "actinide"), (102, "No", "Nobelium", "[259]", "actinide"),
    (103, "Lr", "Lawrencium", "[266]", "actinide"), (104, "Rf", "Rutherfordium", "[267]", "transition"),
    (105, "Db", "Dubnium", "[268]", "transition"), (106, "Sg", "Seaborgium", "[269]", "transition"),
    (107, "Bh", "Bohrium", "[270]", "transition"), (108, "Hs", "Hassium", "[271]", "transition"),
    (109, "Mt", "Meitnerium", "[278]", "transition"), (110, "Ds", "Darmstadtium", "[281]", "transition"),
    (111, "Rg", "Roentgenium", "[282]", "transition"), (112, "Cn", "Copernicium", "[285]", "transition"),
    (113, "Nh", "Nihonium", "[286]", "unknown"), (114, "Fl", "Flerovium", "[289]", "unknown"),
    (115, "Mc", "Moscovium", "[290]", "unknown"), (116, "Lv", "Livermorium", "[293]", "unknown"),
    (117, "Ts", "Tennessine", "[294]", "unknown"), (118, "Og", "Oganesson", "[294]", "unknown"),
]

COLORS = {
    "alkali": "#ff6666", "alkaline": "#ffdead", "transition": "#ffc0c0",
    "post_transition": "#cccccc", "metalloid": "#cccc99", "nonmetal": "#a0ffa0",
    "halogen": "#ffff99", "noble": "#c0ffff", "lanthanide": "#ffbfff",
    "actinide": "#ff99cc", "unknown": "#e8e8e8",
}

# ---------- 中文名 (按原子序数 1..118，一字一元素) ----------
CN_NAMES_STR = ("氢氦锂铍硼碳氮氧氟氖钠镁铝硅磷硫氯氩钾钙钪钛钒铬锰铁钴镍铜锌镓锗砷硒溴氪"
                "铷锶钇锆铌钼锝钌铑钯银镉铟锡锑碲碘氙铯钡镧铈镨钕钷钐铕钆铽镝钬铒铥镱镥"
                "铪钽钨铼锇铱铂金汞铊铅铋钋砹氡钫镭锕钍镤铀镎钚镅锔锫锎锿镄钔锘铹"
                "𬬻𬭊𬭳𬭛𬭶鿏𫟼𬬭鿔鿭𫓧镆𫟷鿬鿫")
CN_NAMES = dict(zip(range(1, 119), CN_NAMES_STR))

# ---------- 电子排布（惰性气体原子实 + 价电子；Rf 之后为理论预测值） ----------
ECONFIG = {
1:"1s¹",2:"1s²",3:"[He]2s¹",4:"[He]2s²",5:"[He]2s²2p¹",6:"[He]2s²2p²",
7:"[He]2s²2p³",8:"[He]2s²2p⁴",9:"[He]2s²2p⁵",10:"[He]2s²2p⁶",
11:"[Ne]3s¹",12:"[Ne]3s²",13:"[Ne]3s²3p¹",14:"[Ne]3s²3p²",15:"[Ne]3s²3p³",
16:"[Ne]3s²3p⁴",17:"[Ne]3s²3p⁵",18:"[Ne]3s²3p⁶",
19:"[Ar]4s¹",20:"[Ar]4s²",21:"[Ar]3d¹4s²",22:"[Ar]3d²4s²",23:"[Ar]3d³4s²",
24:"[Ar]3d⁵4s¹",25:"[Ar]3d⁵4s²",26:"[Ar]3d⁶4s²",27:"[Ar]3d⁷4s²",
28:"[Ar]3d⁸4s²",29:"[Ar]3d¹⁰4s¹",30:"[Ar]3d¹⁰4s²",31:"[Ar]3d¹⁰4s²4p¹",
32:"[Ar]3d¹⁰4s²4p²",33:"[Ar]3d¹⁰4s²4p³",34:"[Ar]3d¹⁰4s²4p⁴",
35:"[Ar]3d¹⁰4s²4p⁵",36:"[Ar]3d¹⁰4s²4p⁶",
37:"[Kr]5s¹",38:"[Kr]5s²",39:"[Kr]4d¹5s²",40:"[Kr]4d²5s²",41:"[Kr]4d⁴5s¹",
42:"[Kr]4d⁵5s¹",43:"[Kr]4d⁵5s²",44:"[Kr]4d⁷5s¹",45:"[Kr]4d⁸5s¹",
46:"[Kr]4d¹⁰",47:"[Kr]4d¹⁰5s¹",48:"[Kr]4d¹⁰5s²",49:"[Kr]4d¹⁰5s²5p¹",
50:"[Kr]4d¹⁰5s²5p²",51:"[Kr]4d¹⁰5s²5p³",52:"[Kr]4d¹⁰5s²5p⁴",
53:"[Kr]4d¹⁰5s²5p⁵",54:"[Kr]4d¹⁰5s²5p⁶",
55:"[Xe]6s¹",56:"[Xe]6s²",57:"[Xe]5d¹6s²",58:"[Xe]4f¹5d¹6s²",59:"[Xe]4f³6s²",
60:"[Xe]4f⁴6s²",61:"[Xe]4f⁵6s²",62:"[Xe]4f⁶6s²",63:"[Xe]4f⁷6s²",
64:"[Xe]4f⁷5d¹6s²",65:"[Xe]4f⁹6s²",66:"[Xe]4f¹⁰6s²",67:"[Xe]4f¹¹6s²",
68:"[Xe]4f¹²6s²",69:"[Xe]4f¹³6s²",70:"[Xe]4f¹⁴6s²",71:"[Xe]4f¹⁴5d¹6s²",
72:"[Xe]4f¹⁴5d²6s²",73:"[Xe]4f¹⁴5d³6s²",74:"[Xe]4f¹⁴5d⁴6s²",
75:"[Xe]4f¹⁴5d⁵6s²",76:"[Xe]4f¹⁴5d⁶6s²",77:"[Xe]4f¹⁴5d⁷6s²",
78:"[Xe]4f¹⁴5d⁹6s¹",79:"[Xe]4f¹⁴5d¹⁰6s¹",80:"[Xe]4f¹⁴5d¹⁰6s²",
81:"[Xe]4f¹⁴5d¹⁰6s²6p¹",82:"[Xe]4f¹⁴5d¹⁰6s²6p²",83:"[Xe]4f¹⁴5d¹⁰6s²6p³",
84:"[Xe]4f¹⁴5d¹⁰6s²6p⁴",85:"[Xe]4f¹⁴5d¹⁰6s²6p⁵",86:"[Xe]4f¹⁴5d¹⁰6s²6p⁶",
87:"[Rn]7s¹",88:"[Rn]7s²",89:"[Rn]6d¹7s²",90:"[Rn]6d²7s²",91:"[Rn]5f²6d¹7s²",
92:"[Rn]5f³6d¹7s²",93:"[Rn]5f⁴6d¹7s²",94:"[Rn]5f⁶7s²",95:"[Rn]5f⁷7s²",
96:"[Rn]5f⁷6d¹7s²",97:"[Rn]5f⁹7s²",98:"[Rn]5f¹⁰7s²",99:"[Rn]5f¹¹7s²",
100:"[Rn]5f¹²7s²",101:"[Rn]5f¹³7s²",102:"[Rn]5f¹⁴7s²",103:"[Rn]5f¹⁴7s²7p¹",
104:"[Rn]5f¹⁴6d²7s²",105:"[Rn]5f¹⁴6d³7s²",106:"[Rn]5f¹⁴6d⁴7s²",
107:"[Rn]5f¹⁴6d⁵7s²",108:"[Rn]5f¹⁴6d⁶7s²",109:"[Rn]5f¹⁴6d⁷7s²",
110:"[Rn]5f¹⁴6d⁸7s²",111:"[Rn]5f¹⁴6d⁹7s²",112:"[Rn]5f¹⁴6d¹⁰7s²",
113:"[Rn]5f¹⁴6d¹⁰7s²7p¹",114:"[Rn]5f¹⁴6d¹⁰7s²7p²",
115:"[Rn]5f¹⁴6d¹⁰7s²7p³",116:"[Rn]5f¹⁴6d¹⁰7s²7p⁴",
117:"[Rn]5f¹⁴6d¹⁰7s²7p⁵",118:"[Rn]5f¹⁴6d¹⁰7s²7p⁶",
}

MAIN_PREF = ["Microsoft YaHei", "Microsoft YaHei UI", "PingFang SC",
             "Hiragino Sans GB", "Noto Sans CJK SC", "Source Han Sans SC",
             "SimHei", "SimSun", "Microsoft JhengHei", "Noto Sans SC",
             "WenQuanYi Micro Hei"]
# ---------- 老式族编号 (CAS / 国内教材): 1-18 族 -> IA..VIIIA ----------
GROUP_ROMAN = {1:"IA", 2:"IIA", 3:"IIIB", 4:"IVB", 5:"VB", 6:"VIB", 7:"VIIB",
               8:"VIII", 9:"VIII", 10:"VIII", 11:"IB", 12:"IIB", 13:"IIIA",
               14:"IVA", 15:"VA", 16:"VIA", 17:"VIIA", 18:"VIIIA"}


def scan_fonts():
    """返回 {字体文件路径: (字体族名, 可覆盖的中文字集合)}"""
    out = {}
    for entry in fm.fontManager.ttflist:
        p = entry.fname
        if p in out:
            continue
        try:
            f = ft2font.FT2Font(p)
            cov = {ch for ch in CN_NAMES_STR if f.get_char_index(ord(ch)) != 0}
            out[p] = (f.family_name, cov)
        except Exception:
            continue
    return out


def choose_fonts():
    """挑选主中文字体 + 为每个汉字指定一个能显示它的字体路径。
    返回 (主字体路径, 字体字典, 字->路径映射)。"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    local = os.path.join(script_dir, "cjk.ttf")
    if os.path.exists(local):
        try:
            fm.fontManager.addfont(local)
        except Exception:
            pass
    fonts = scan_fonts()
    if os.path.exists(local):
        try:
            f = ft2font.FT2Font(local)
            fonts[local] = (f.family_name,
                            {ch for ch in CN_NAMES_STR if f.get_char_index(ord(ch)) != 0})
        except Exception:
            pass
    if not fonts:
        return None, {}, {}
    ranked = sorted(fonts.items(), key=lambda kv: -len(kv[1][1]))
    main_path = local if os.path.exists(local) else None
    if main_path is None:
        for pref in MAIN_PREF:
            for path, (fam, cov) in fonts.items():
                if fam == pref or fam.startswith(pref):
                    main_path = path
                    break
            if main_path:
                break
    if main_path is None:
        main_path = ranked[0][0]
    main_cov = fonts.get(main_path, ("", set()))[1]
    mapping = {}
    for ch in CN_NAMES_STR:
        if ch in main_cov:
            mapping[ch] = main_path
            continue
        for path, (fam, cov) in ranked:
            if ch in cov:
                mapping[ch] = path
                break
        else:
            mapping[ch] = None
    return main_path, fonts, mapping


def build_positions():
    """返回 (主表, f区): 原子序数 -> (行, 列)，行 1..7 自上而下 = 周期，列 1..18 = 族。"""
    main, fb = {}, {}
    main[1] = (1, 1); main[2] = (1, 18)
    for c, z in zip([1, 2, 13, 14, 15, 16, 17, 18], range(3, 11)): main[z] = (2, c)
    for c, z in zip([1, 2, 13, 14, 15, 16, 17, 18], range(11, 19)): main[z] = (3, c)
    for z in range(19, 37): main[z] = (4, z - 18)
    for z in range(37, 55): main[z] = (5, z - 36)
    main[55] = (6, 1); main[56] = (6, 2)
    for i, z in enumerate(range(72, 87)): main[z] = (6, 4 + i)     # Hf..Rn -> 族 4..18
    main[87] = (7, 1); main[88] = (7, 2)
    for i, z in enumerate(range(104, 119)): main[z] = (7, 4 + i)   # Rf..Og -> 族 4..18
    for i, z in enumerate(range(57, 72)): fb[z] = (0, i)           # 镧系, 15 格
    for i, z in enumerate(range(89, 104)): fb[z] = (1, i)          # 锕系
    return main, fb


def main():
    # ---- 字体准备 ----
    main_path, fonts, mapping = choose_fonts()
    cn_props, missing = {}, []
    for z, ch in CN_NAMES.items():
        p = mapping.get(ch)
        if p:
            cn_props[z] = fm.FontProperties(fname=p)
        else:
            missing.append(z)
    if main_path:
        print("主中文字体:", fonts[main_path][0], "->", main_path)
    else:
        print("错误: 未找到任何中文字体，中文名将无法显示（英文部分不受影响）。")
    if missing:
        by_z = {e[0]: e for e in ELEMENTS}
        print("警告: 以下元素的中文名没有可用字形，将被留空:")
        print("  " + ", ".join(f"{z}{by_z[z][1]}({CN_NAMES[z]})" for z in missing))

    # ---- 页面: A3 横向 (420 x 297 mm) ----
    W_IN, H_IN = 420 / 25.4, 297 / 25.4
    fig = plt.figure(figsize=(W_IN, H_IN))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN)
    ax.set_aspect("equal"); ax.axis("off")

    M_SIDE = 0.36
    GRID_W = W_IN - 2 * M_SIDE
    CELL_W = GRID_W / 18.0
    CELL_H = 0.95
    GAP = 0.34
    F_CELL_H = 0.86
    GRID_TOP = H_IN - 1.42
    F_TOP = GRID_TOP - 7 * CELL_H - GAP
    by_z = {e[0]: e for e in ELEMENTS}
    main_pos, fb_pos = build_positions()

    def draw_cell(x, y, w, h, e, econf, fs_sym, fs_name, fs_cfg, fs_small, cn_fp=None):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=COLORS[e[4]],
                               edgecolor="black", linewidth=0.9))
        cx = x + w / 2
        # 左上角原子序数 / 右上角中文名
        ax.text(x + 0.055 * w, y + h - 0.075 * h, str(e[0]), ha="left", va="center",
                fontsize=fs_small, fontweight="bold")
        cn = CN_NAMES.get(e[0], "")
        if cn and cn_fp is not None:
            ax.text(x + 0.945 * w, y + h - 0.075 * h, cn, ha="right", va="center",
                    fontsize=fs_small, color="0.15", fontproperties=cn_fp)
        # 符号 / 英文名 / 电子排布 / 相对原子质量
        ax.text(cx, y + 0.63 * h, e[1], ha="center", va="center",
                fontsize=fs_sym, fontweight="bold")
        ax.text(cx, y + 0.43 * h, e[2], ha="center", va="center", fontsize=fs_name)
        renderer = fig.canvas.get_renderer()
        fs = fs_cfg
        while fs > 3.2:                     # 电子排布自动缩字号，保证不超出格子
            t = ax.text(cx, y + 0.225 * h, econf, ha="center", va="center",
                        fontsize=fs, color="0.05")
            if t.get_window_extent(renderer).width / fig.dpi <= 0.88 * w:
                break
            t.remove()
            fs -= 0.25
        else:
            if fs <= 3.2:
                ax.text(cx, y + 0.225 * h, econf, ha="center", va="center",
                        fontsize=3.2, color="0.05")
        ax.text(cx, y + 0.06 * h, e[3], ha="center", va="center", fontsize=fs_small)

    # ---- 主表 ----
    for z, (r, c) in main_pos.items():
        x = M_SIDE + (c - 1) * CELL_W
        y = GRID_TOP - r * CELL_H
        draw_cell(x, y, CELL_W, CELL_H, by_z[z], ECONFIG.get(z, ""),
                  15.5, 7.0, 5.4, 7.6, cn_props.get(z))

    # ---- 第 6、7 周期第 3 族的占位格 ----
    for r, t1, t2, key in [(6, "57-71", "La-Lu", "lanthanide"),
                           (7, "89-103", "Ac-Lr", "actinide")]:
        x = M_SIDE + 2 * CELL_W
        y = GRID_TOP - r * CELL_H
        ax.add_patch(Rectangle((x, y), CELL_W, CELL_H, facecolor=COLORS[key],
                               edgecolor="black", linewidth=0.9, linestyle="--"))
        ax.text(x + CELL_W / 2, y + 0.63 * CELL_H, t1, ha="center", va="center",
                fontsize=9, fontweight="bold")
        ax.text(x + CELL_W / 2, y + 0.30 * CELL_H, t2, ha="center", va="center", fontsize=7.5)

    # ---- 镧系 / 锕系 (对齐族 3..17) ----
    for z, (r, c) in fb_pos.items():
        x = M_SIDE + (2 + c) * CELL_W
        y = F_TOP - (r + 1) * F_CELL_H
        draw_cell(x, y, CELL_W, F_CELL_H, by_z[z], ECONFIG.get(z, ""),
                  13, 6.2, 4.7, 6.8, cn_props.get(z))

        for r, label in [(0, "f-block  Lanthanides"), (1, "f-block  Actinides")]:
             y = F_TOP - (r + 0.5) * F_CELL_H
             ax.text(M_SIDE + 0.05, y, label, ha="left", va="center",
        
                fontsize=8.5, fontweight="bold", color="0.15")
        
        # ---- 族号：上排罗马字(IA..VIIIA)，下排阿拉伯数字(1-18) ----
    for g in range(1, 19):
        ax.text(M_SIDE + (g - 0.5) * CELL_W, GRID_TOP + 0.10, str(g),
                ha="center", va="center", fontsize=9, color="0.2")
    for g in range(1, 19):
        if g in (9, 10):
            continue                      # VIII 跨第 8、9、10 三列，只在第 8 列处画一次
        if g == 8:
            x0 = M_SIDE + 7 * CELL_W
            x1 = M_SIDE + 10 * CELL_W
            ax.text((x0 + x1) / 2, GRID_TOP + 0.32, GROUP_ROMAN[g],
                    ha="center", va="center", fontsize=8.5, fontweight="bold", color="0.1")
        else:
            ax.text(M_SIDE + (g - 0.5) * CELL_W, GRID_TOP + 0.32, GROUP_ROMAN[g],
                    ha="center", va="center", fontsize=8.5, fontweight="bold", color="0.1")
    # ---- 周期号（行，左侧 1-7，加粗醒目） ----
    for p in range(1, 8):
        ax.text(M_SIDE - 0.20, GRID_TOP - (p - 0.5) * CELL_H, str(p),
                ha="center", va="center", fontsize=10, fontweight="bold", color="0.1")

    # ---- s/d/p 区标注 ----
    for bname, g0, g1 in [("s", 1, 2), ("d", 3, 12), ("p", 13, 18)]:
        x0 = M_SIDE + (g0 - 1) * CELL_W
        x1 = M_SIDE + g1 * CELL_W
        ax.text((x0 + x1) / 2, GRID_TOP + 0.54, bname + "-block",
                ha="center", va="center", fontsize=8.5, fontstyle="italic", color="0.3")
    # ---- 标题 ----
    ax.text(W_IN / 2, H_IN - 0.40, "Periodic Table of the Elements",
            ha="center", va="center", fontsize=22, fontweight="bold")
    ax.text(W_IN / 2, H_IN - 0.62,
            "Each cell: atomic number, symbol, English name, Chinese name, electron configuration, relative atomic mass",
            ha="center", va="center", fontsize=10.5, color="0.2")

    # ---- 图例 ----
    legend = [("Alkali metals", "alkali"), ("Alkaline earth metals", "alkaline"),
              ("Transition metals", "transition"), ("Post-transition metals", "post_transition"),
              ("Metalloids", "metalloid"), ("Reactive nonmetals", "nonmetal"),
              ("Halogens", "halogen"), ("Noble gases", "noble"),
              ("Lanthanides", "lanthanide"), ("Actinides", "actinide"),
              ("Unknown properties", "unknown")]
    for row_items, y in [(legend[:6], 1.36), (legend[6:], 1.06)]:
        n = len(row_items)
        for i, (label, key) in enumerate(row_items):
            cx = W_IN * (i + 0.5) / n
            sw, sh = 0.30, 0.16
            block = sw + 0.08 + len(label) * 0.059
            sx = cx - block / 2
            ax.add_patch(Rectangle((sx, y - sh / 2), sw, sh, facecolor=COLORS[key],
                                   edgecolor="black", linewidth=0.7))
            ax.text(sx + sw + 0.08, y, label, ha="left", va="center", fontsize=8.5)

    # ---- 脚注 ----
    ax.text(W_IN / 2, 0.72,
            "Atomic masses are IUPAC standard atomic weights (abridged, CIAAW 2024); [ ] = mass number "
            "of the most stable isotope. Electron configurations use noble-gas core notation ([He], [Ne], "
            "[Ar], ...); values for Rf-Og and Lr (7p¹) are predicted.",
            ha="center", va="center", fontsize=8, style="italic", color="0.25")

    # ---- 保存（输出到脚本所在目录；PNG 保存失败时自动兜底） ----
    try:
        out_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        out_dir = os.getcwd()
    pdf_path = os.path.join(out_dir, "periodic_table_A3.pdf")
    png_path = os.path.join(out_dir, "periodic_table_A3.png")
    print("输出目录:", out_dir)
    fig.savefig(pdf_path)
    print("已保存:", pdf_path)
    try:
        fig.savefig(png_path, dpi=300)
    except OSError as err:
        print("PNG 常规保存失败，改用内置 PNG 写入器……")
        print("  原因:", err)
        try:
            import numpy as np
            import matplotlib._png as mpl_png
            fig.canvas.draw()
            buf = np.asarray(fig.canvas.renderer.buffer_rgba())
            with open(png_path, "wb") as fh:
                mpl_png.write_png(buf, fh, dpi=(300, 300))
        except OSError as err2:
            print("PNG 保存仍然失败:", err2)
            print("当前工作目录:", os.getcwd())
            png_path = None
    if png_path:
        print("已保存:", png_path)
    plt.close(fig)
    print("完成。打印请使用 periodic_table_A3.pdf（A3 横向、100% 缩放、彩色）")


if __name__ == "__main__":
    main()
