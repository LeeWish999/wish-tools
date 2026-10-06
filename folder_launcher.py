# -*- coding: utf-8 -*-
"""
FolderLauncher —— 文件夹快捷启动器（Windows）
功能：添加常用文件夹 -> 单击一键在资源管理器中打开，快捷方式持久保存。

可选依赖（启用拖拽添加功能）：pip install tkinterdnd2
打包（便于固定到任务栏/开始菜单）：
    pip install pyinstaller
    pyinstaller --onefile --windowed --clean --name FolderLauncher FolderLauncher.py
    （若装了 tkinterdnd2，追加：--collect-all tkinterdnd2）
"""
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

APP_NAME = "FolderLauncher"
APP_TITLE = "文件夹快捷启动器"

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


def app_dir():
    """exe / 脚本所在目录。"""
    if getattr(sys, "frozen", False):            # PyInstaller 打包后
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def config_path():
    """配置文件：优先 exe 同目录（便携），不可写则退回 %APPDATA%。"""
    path = os.path.join(app_dir(), "folders.json")
    try:
        with open(path, "a", encoding="utf-8"):
            pass
        return path
    except OSError:
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "folders.json")


def load_items():
    try:
        with open(config_path(), encoding="utf-8") as f:
            data = json.load(f)
        return [d for d in data if isinstance(d, dict) and d.get("path")]
    except (OSError, json.JSONDecodeError):
        return []


def save_items(items):
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def open_in_explorer(path):
    """在资源管理器中打开文件夹。"""
    if not os.path.isdir(path):
        return False
    if sys.platform == "win32":
        os.startfile(path)                       # Windows
    else:
        subprocess.Popen(["xdg-open", path])
    return True


class App(tk.Tk if not HAS_DND else TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("460x600")
        self.minsize(360, 320)

        self.items = load_items()

        # ---- 顶部工具栏 ----
        bar = ttk.Frame(self, padding=(8, 8, 8, 4))
        bar.pack(fill="x")
        ttk.Button(bar, text="＋ 添加文件夹", command=self.add_folder).pack(side="left")
        ttk.Button(bar, text="按名称排序", command=self.sort_by_name).pack(side="left", padx=(6, 0))
        self.count_var = tk.StringVar()
        tk.Label(bar, textvariable=self.count_var, anchor="e").pack(side="right")

        # ---- 中间可滚动列表 ----
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=8, pady=(4, 0))
        self.canvas = tk.Canvas(wrap, highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = ttk.Frame(self.canvas)
        self.win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self.win_id, width=e.width))
        self._bind_wheel(self.canvas)
        self._bind_wheel(self.inner)

        # ---- 底部状态栏 ----
        self.status = tk.StringVar(value="提示：单击打开文件夹；右键管理；右键空白处更多选项。")
        tk.Label(self, textvariable=self.status, anchor="w", relief="sunken",
                 bd=1, padx=8, pady=4).pack(fill="x", side="bottom")

        # ---- 右键菜单 ----
        self._menu_row = None                     # 当前右键操作的行号
        self.menu_item = tk.Menu(self, tearoff=0)
        self.menu_item.add_command(label="打开", command=self.menu_open)
        self.menu_item.add_command(label="重命名（仅改显示名）", command=self.menu_rename)
        self.menu_item.add_command(label="复制路径", command=self.menu_copy_path)
        self.menu_item.add_separator()
        self.menu_item.add_command(label="删除", command=self.menu_remove)
        self.menu_blank = tk.Menu(self, tearoff=0)
        self.menu_blank.add_command(label="添加文件夹…", command=self.add_folder)
        self.menu_blank.add_command(label="打开数据文件所在位置", command=self.open_config_dir)

        self.canvas.bind("<Button-3>", self.popup_blank)
        self.inner.bind("<Button-3>", self.popup_blank)

        # ---- 拖拽添加（可选） ----
        if HAS_DND:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", self.on_drop)
            except Exception:
                pass

        # ---- 窗口图标（可选）：exe 同目录放 app.ico 会自动使用 ----
        ico = os.path.join(app_dir(), "app.ico")
        if os.path.exists(ico):
            try:
                self.iconbitmap(ico)
            except tk.TclError:
                pass

        self.rebuild()

    # ---------- 列表渲染 ----------
    def rebuild(self):
        for w in self.inner.winfo_children():
            w.destroy()
        if not self.items:
            ttk.Label(self.inner, anchor="center", padding=24,
                      text="还没有文件夹。\n点击上方“＋ 添加文件夹”，或把文件夹拖进窗口。",
                      justify="center").pack(fill="x", expand=True, pady=40)
        else:
            for idx, item in enumerate(self.items):
                self._make_row(idx, item)
        self.count_var.set(f"共 {len(self.items)} 项")
        self.inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _make_row(self, idx, item):
        path = item.get("path", "")
        name = item.get("name") or os.path.basename(path.rstrip("\\/")) or path
        row = ttk.Frame(self.inner, padding=(4, 2))
        row.pack(fill="x")
        btn = tk.Button(row, text=name, anchor="w", padx=10, pady=6,
                        relief="flat", bd=0, cursor="hand2",
                        command=lambda p=path: self.on_open(p))
        btn.pack(fill="x")
        btn.bind("<Button-3>", lambda e, i=idx: self.popup_item(e, i))
        row.bind("<Button-3>", lambda e, i=idx: self.popup_item(e, i))
        btn.bind("<Enter>", lambda e, b=btn, p=path: self._enter_row(b, p))
        btn.bind("<Leave>", lambda e, b=btn: self._leave_row(b))
        row.bind("<Enter>", lambda e, p=path: self.status.set(p))
        row.bind("<Leave>", lambda e: self.status.set(""))
        self._bind_wheel(btn)
        self._bind_wheel(row)

    def _enter_row(self, btn, path):
        btn.configure(bg="#e5f1fb", activebackground="#cce4f7")
        self.status.set(path)

    def _leave_row(self, btn):
        btn.configure(bg="SystemButtonFace")
        self.status.set("")

    # ---------- 基本操作 ----------
    def on_open(self, path):
        if open_in_explorer(path):
            self.status.set(path)
            return
        if messagebox.askyesno("文件夹不存在",
                               f"找不到文件夹：\n{path}\n\n是否从列表中移除？"):
            self.items = [it for it in self.items if it.get("path") != path]
            save_items(self.items)
            self.rebuild()

    def add_folder(self):
        path = filedialog.askdirectory(parent=self, title="选择要添加的文件夹")
        if path:
            self.add_path(path)

    def add_path(self, path):
        path = os.path.normpath(path)
        if any(os.path.normcase(it.get("path", "")) == os.path.normcase(path)
               for it in self.items):
            messagebox.showinfo(APP_TITLE, "该文件夹已在列表中。")
            return
        self.items.append({"name": os.path.basename(path.rstrip("\\/")) or path,
                           "path": path})
        save_items(self.items)
        self.rebuild()
        self.canvas.yview_moveto(1.0)             # 滚到底部看到新项

    def sort_by_name(self):
        self.items.sort(key=lambda it: (it.get("name") or "").lower())
        save_items(self.items)
        self.rebuild()

    def open_config_dir(self):
        path = config_path()
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", path])
        else:
            open_in_explorer(os.path.dirname(path))

    # ---------- 右键菜单 ----------
    def _sel(self):
        if self._menu_row is None or not (0 <= self._menu_row < len(self.items)):
            return None
        return self.items[self._menu_row]

    def popup_item(self, event, idx):
        self._menu_row = idx
        try:
            self.menu_item.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_item.grab_release()

    def popup_blank(self, event):
        self._menu_row = None
        try:
            self.menu_blank.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_blank.grab_release()

    def menu_open(self):
        it = self._sel()
        if it:
            self.on_open(it["path"])

    def menu_rename(self):
        it = self._sel()
        if not it:
            return
        name = simpledialog.askstring("重命名", "显示名称：",
                                      initialvalue=it.get("name", ""), parent=self)
        if name and name.strip():
            it["name"] = name.strip()
            save_items(self.items)
            self.rebuild()

    def menu_copy_path(self):
        it = self._sel()
        if it:
            self.clipboard_clear()
            self.clipboard_append(it["path"])
            self.status.set("已复制：" + it["path"])

    def menu_remove(self):
        it = self._sel()
        if it and messagebox.askyesno("删除",
                                      f"删除快捷方式：{it.get('name', '')}\n"
                                      f"（不会删除磁盘上的文件夹）"):
            self.items.pop(self._menu_row)
            save_items(self.items)
            self.rebuild()

    # ---------- 拖拽与滚轮 ----------
    def on_drop(self, event):
        added = 0
        for raw in self.tk.splitlist(event.data):
            p = raw.strip("{}") if raw.startswith("{") else raw
            if os.path.isdir(p):
                self.add_path(p)
                added += 1
        if not added:
            messagebox.showinfo(APP_TITLE, "仅支持拖入文件夹。")

    def _bind_wheel(self, widget):
        widget.bind("<MouseWheel>", self._on_wheel)
        widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
