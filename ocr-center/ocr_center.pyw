# -*- coding: utf-8 -*-
# ocr_center.pyw —— 公式书数字化一站式工具
# 功能：① PDF→图片 ② 图片→PDF ③ OCR→LaTeX ④ 全自动流水线
# 保存编码 UTF-8，双击运行。

import base64, os, queue, shutil, subprocess, sys, threading, time, tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# ---------- 路径与环境（全部相对本文件，换电脑 / 换目录可用） ----------
BASE     = os.path.dirname(os.path.abspath(__file__))                        # 程序所在目录
OUT_ROOT = os.environ.get("OCR_OUT_ROOT") or os.path.join(BASE, "output")    # 输出总目录（可用环境变量覆盖）
W_PDF2PNG = os.path.join(BASE, "pdf2png_worker.py")
W_IMG2PDF = os.path.join(BASE, "img2pdf_worker.py")
W_OCR     = os.path.join(BASE, "ocr_worker.py")
DIR_PNG   = os.path.join(OUT_ROOT, "pdf-to-png")                             # ① PDF→图片 输出
DIR_PDF   = os.path.join(OUT_ROOT, "img-to-pdf")                             # ② 图片→PDF 输出
DIR_LATEX = os.path.join(OUT_ROOT, "ocr")                                    # ③ OCR 输出


def find_python():
    """选 worker 用的 python.exe：① 环境变量 OCR_PYTHON ② 程序旁的 .venv/venv ③ 当前解释器。"""
    env = os.environ.get("OCR_PYTHON")
    if env and os.path.isfile(env):
        return env
    for name in (".venv", "venv", "env"):
        cand = os.path.join(BASE, name, "Scripts", "python.exe")
        if os.path.isfile(cand):
            return cand
    exe = sys.executable or "python"
    if os.path.basename(exe).lower() == "pythonw.exe":
        cand = os.path.join(os.path.dirname(exe), "python.exe")
        if os.path.isfile(cand):
            return cand
    return exe


VENV_PY  = find_python()                    # 运行 worker 用的 python.exe
VENV_PYW = VENV_PY                          # 启动本程序用（无窗口）
if VENV_PY.lower().endswith("python.exe"):
    _pyw = VENV_PY[:-len("python.exe")] + "pythonw.exe"
    if os.path.isfile(_pyw):
        VENV_PYW = _pyw

TASK_TITLE = {
    "pdf2png": "① PDF 转图片",
    "img2pdf": "② 图片转 PDF",
    "ocr":     "③ OCR 转 LaTeX",
    "pipe":    "④ 全自动流水线",
}

class App:
    def __init__(self, root):
        self.root = root
        root.title("OCR 中心 —— 公式书数字化")
        root.geometry("900x600")
        self.running = False
        self.q = queue.Queue()
        self.run_dirs = []   # 本次任务发现的中间文件夹
        self.run_pdfs = []   # 本次任务发现的中间 PDF
        self.build_ui()
        self.root.after(100, self.poll_q)
        self.check_env()

    def build_ui(self):
        top = tk.Frame(self.root); top.pack(fill="x", padx=10, pady=8)
        tk.Label(top, text="OCR 中心", font=("Microsoft YaHei", 16, "bold")).pack(anchor="w")
        tk.Label(top, text="图片 → " + DIR_PNG + "\n图片型PDF → " + DIR_PDF + "\nLaTeX → " + DIR_LATEX,
                 justify="left", font=("Microsoft YaHei", 8), fg="#555").pack(anchor="w")

        btns = tk.Frame(self.root); btns.pack(fill="x", padx=10, pady=4)
        self.task_btns = []
        specs = [
            ("pdf2png", "① PDF → 图片\n(单个 / 批量)"),
            ("img2pdf", "② 图片 → PDF\n(单个 / 批量)"),
            ("ocr",     "③ OCR → LaTeX\n(单个 / 批量)"),
            ("pipe",    "④ 全自动流水线\nPDF→图片→PDF→OCR"),
        ]
        for key, text in specs:
            b = tk.Button(btns, text=text, height=2, width=20,
                          font=("Microsoft YaHei", 10),
                          command=lambda k=key: self.start_task(k))
            b.pack(side="left", padx=6)
            self.task_btns.append(b)

        row2 = tk.Frame(self.root); row2.pack(fill="x", padx=10, pady=2)
        tk.Button(row2, text="固定到开始菜单", width=16,
                  command=self.install_to_start).pack(side="left", padx=4)
        tk.Button(row2, text="打开输出目录", width=16,
                  command=self.open_base).pack(side="left", padx=4)
        tk.Button(row2, text="退出", width=16,
                  command=self.on_exit).pack(side="left", padx=4)

        self.logbox = scrolledtext.ScrolledText(self.root, state="disabled",
                        font=("Consolas", 9), wrap="word")
        self.logbox.pack(fill="both", expand=True, padx=10, pady=6)
        self.logbox.tag_configure("err", foreground="#c00000")
        self.logbox.tag_configure("ok", foreground="#1e7b1e")
        self.status = tk.Label(self.root, text="就绪", anchor="w", font=("Microsoft YaHei", 9))
        self.status.pack(fill="x", padx=10, pady=(0, 6))

    def check_env(self):
        self.insert_log("[信息] worker 解释器：" + VENV_PY)
        if not os.path.isfile(VENV_PY):
            self.insert_log("[错误] 未找到可用的 python.exe：" + VENV_PY, "err")
        for w, name in [(W_PDF2PNG, "pdf2png_worker.py"),
                        (W_IMG2PDF, "img2pdf_worker.py"),
                        (W_OCR, "ocr_worker.py")]:
            if not os.path.isfile(w):
                self.insert_log("[错误] 缺少脚本：" + name, "err")

    def log(self, msg):
        self.q.put(("[LOG]", time.strftime("%H:%M:%S") + " " + msg))

    def insert_log(self, text, tag=None):
        self.logbox.config(state="normal")
        self.logbox.insert("end", text + "\n", tag or ())
        self.logbox.see("end")
        self.logbox.config(state="disabled")

    def poll_q(self):
        try:
            while True:
                item = self.q.get_nowait()
                if isinstance(item, tuple):
                    if item[0] == "DONE":
                        self.on_done(item[1])
                    else:
                        self.insert_log(item[1])
                else:
                    tag = "err" if item.startswith("[错误]") else ("ok" if item.startswith("[完成]") else None)
                    self.insert_log(item, tag)
        except queue.Empty:
            pass
        self.root.after(100, self.poll_q)

    def ask_mode(self, title):
        d = tk.Toplevel(self.root); d.title(title); d.resizable(False, False)
        d.transient(self.root); d.grab_set()
        res = {"v": None}
        tk.Label(d, text="请选择处理方式：", font=("Microsoft YaHei", 11)).pack(padx=30, pady=(16, 4))
        f = tk.Frame(d); f.pack(padx=10, pady=8)
        tk.Button(f, text="[1] 单个", width=12, command=lambda: (res.__setitem__("v", "single"), d.destroy())).pack(side="left", padx=6)
        tk.Button(f, text="[2] 批量", width=12, command=lambda: (res.__setitem__("v", "batch"), d.destroy())).pack(side="left", padx=6)
        tk.Button(f, text="取消", width=12, command=lambda: (res.__setitem__("v", None), d.destroy())).pack(side="left", padx=6)
        d.geometry("+%d+%d" % (self.root.winfo_rootx() + 250, self.root.winfo_rooty() + 160))
        self.root.wait_window(d)
        return res["v"]

    def pick_inputs(self, key, mode):
        if key == "img2pdf":
            if mode == "single":
                folder = filedialog.askdirectory(title="选择包含图片的文件夹")
                return [folder] if folder else None
            parent = filedialog.askdirectory(title="选择父文件夹（每个子文件夹合成一个 PDF）")
            if not parent: return None
            subs = [os.path.join(parent, d) for d in os.listdir(parent)
                    if os.path.isdir(os.path.join(parent, d))]
            return subs if subs else None
        # 其余功能输入 PDF
        if mode == "single":
            f = filedialog.askopenfilename(title="选择 PDF 文件",
                    filetypes=[("PDF 文件", "*.pdf")])
            return [f] if f else None
        folder = filedialog.askdirectory(title="选择包含 PDF 的文件夹")
        if not folder: return None
        pdfs = [os.path.join(folder, d) for d in os.listdir(folder)
                if d.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder, d))]
        return pdfs if pdfs else None

    def start_task(self, key):
        if self.running:
            return
        mode = self.ask_mode(TASK_TITLE[key])
        if not mode:
            return
        inputs = self.pick_inputs(key, mode)
        if not inputs:
            messagebox.showinfo("提示", "没有找到可处理的文件。")
            return
        self.running = True
        for b in self.task_btns:
            b.config(state="disabled")
        self.status.config(text="运行中：" + TASK_TITLE[key])
        threading.Thread(target=self.task_loop, args=(key, mode, inputs), daemon=True).start()

    def exec_cmd(self, args):
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self.log("执行: " + os.path.basename(args[0]))
        p = subprocess.Popen([VENV_PY] + args, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                             errors="replace", env=env, creationflags=flags)
        for line in p.stdout:
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("[目录] "):
                self.run_dirs.append(line[len("[目录] "):].strip())
            elif line.startswith("[文件] "):
                self.run_pdfs.append(line[len("[文件] "):].strip())
            self.q.put(line)
        p.wait()
        return p.returncode

    def task_loop(self, key, mode, inputs):
        d0, f0 = len(self.run_dirs), len(self.run_pdfs)
        ok = True
        try:
            if key == "pdf2png":
                for pdf in inputs:
                    if self.exec_cmd([W_PDF2PNG, pdf]) != 0:
                        self.log("[错误] 失败: " + pdf); ok = False
            elif key == "img2pdf":
                for folder in inputs:
                    if self.exec_cmd([W_IMG2PDF, folder]) != 0:
                        self.log("[错误] 失败: " + folder); ok = False
            elif key == "ocr":
                self.log("[提示] 请确认 Umi-OCR 已完全退出（托盘右键退出），否则显存不足。")
                if self.exec_cmd([W_OCR] + inputs) != 0:
                    ok = False
            elif key == "pipe":
                pipe_pdfs = []
                for pdf in inputs:
                    if self.exec_cmd([W_PDF2PNG, pdf]) != 0:
                        continue
                    pngdir = self.run_dirs[-1]
                    if self.exec_cmd([W_IMG2PDF, pngdir]) != 0:
                        continue
                    pipe_pdfs.append(self.run_pdfs[-1])
                if pipe_pdfs:
                    self.log("[提示] 请确认 Umi-OCR 已完全退出（托盘右键退出），否则显存不足。")
                    if self.exec_cmd([W_OCR] + pipe_pdfs) != 0:
                        ok = False
        except Exception as e:
            self.log("[错误] " + str(e)); ok = False
        dirs = self.run_dirs[d0:]
        pdfs = self.run_pdfs[f0:]
        self.q.put(("DONE", (key, mode, dirs, pdfs, ok)))

    def on_done(self, data):
        key, mode, dirs, pdfs, ok = data
        self.running = False
        for b in self.task_btns:
            b.config(state="normal")
        self.status.config(text="就绪")
        if ok and key in ("pdf2png", "pipe"):
            self.cleanup_dialog(key, dirs, pdfs)

    def cleanup_dialog(self, key, dirs, pdfs):
        del_dirs = dirs[:]
        del_files = pdfs[:] if key == "pipe" else []
        if not del_dirs and not del_files:
            return
        d = tk.Toplevel(self.root)
        d.title("是否保留中间数据？")
        d.transient(self.root); d.grab_set()
        tk.Label(d, text="任务已完成！中间数据（删除后不影响最终 OCR 结果）：\n"
                         "勾选的项目将被删除，不勾选则全部保留。",
                 font=("Microsoft YaHei", 10), justify="left").pack(padx=20, pady=(14, 6), anchor="w")
        v1 = tk.BooleanVar(value=False); v2 = tk.BooleanVar(value=False)
        if del_dirs:
            tk.Checkbutton(d, text="删除图片文件夹（%d 个，位于输出目录 pdf-to-png）" % len(del_dirs),
                           variable=v1, font=("Microsoft YaHei", 10)).pack(anchor="w", padx=20, pady=2)
        if del_files:
            tk.Checkbutton(d, text="删除图片型 PDF（%d 个，位于输出目录 img-to-pdf）" % len(del_files),
                           variable=v2, font=("Microsoft YaHei", 10)).pack(anchor="w", padx=20, pady=2)
        f = tk.Frame(d); f.pack(pady=10)
        def ok_cb():
            d.destroy()
            if v1.get():
                for p in del_dirs:
                    try:
                        shutil.rmtree(p); self.log("[清理] 已删除文件夹: " + os.path.basename(p))
                    except Exception:
                        self.log("[清理] 删除失败: " + p)
            if v2.get():
                for p in del_files:
                    try:
                        os.remove(p); self.log("[清理] 已删除: " + os.path.basename(p))
                    except Exception:
                        self.log("[清理] 删除失败: " + p)
        tk.Button(f, text="确认", width=12, command=ok_cb).pack(side="left", padx=8)
        tk.Button(f, text="全部保留", width=12, command=d.destroy).pack(side="left", padx=8)
        d.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 120))

    def install_to_start(self):
        target = VENV_PYW if os.path.exists(VENV_PYW) else VENV_PY
        script = os.path.abspath(__file__)   # 用自身路径，不写死文件名
        ps = ("$ws = New-Object -ComObject WScript.Shell; "
              "$lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Programs') + '\\OCR 中心.lnk'); "
              "$lnk.TargetPath = '%s'; $lnk.Arguments = '\"%s\"'; "
              "$lnk.WorkingDirectory = '%s'; $lnk.Description = 'OCR 中心'; "
              "$lnk.Save(); Write-Output 'OK'" % (target, script, BASE))
        enc = base64.b64encode(ps.encode("utf-16-le")).decode("ascii")
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-EncodedCommand", enc], capture_output=True,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        out = (r.stdout or b"").decode("utf-8", "ignore")
        if "OK" in out:
            messagebox.showinfo("安装完成",
                "已加入开始菜单：OCR 中心\n\n固定方法：\n"
                "1) 按 Win 键，输入 OCR\n"
                "2) 右键 “OCR 中心”\n"
                "3) 固定到“开始”屏幕（也可“更多 → 固定到任务栏”）")
        else:
            messagebox.showerror("安装失败", "创建快捷方式失败（请确认本机 PowerShell 可用）。\n"
                                + (r.stderr or b"").decode("utf-8", "ignore")[:200])

    def open_base(self):
        try:
            os.makedirs(OUT_ROOT, exist_ok=True)
            os.startfile(OUT_ROOT)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def on_exit(self):
        if self.running and not messagebox.askyesno("确认", "任务正在运行，确定要退出吗？"):
            return
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
