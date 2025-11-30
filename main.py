#!/usr/bin/env python3  
# -*- coding: utf-8 -*-  

import tkinter as tk  
from tkinter import ttk, filedialog, messagebox  
from PIL import Image  
import configparser  
from pathlib import Path  
import os, sys  

# 支持的 ICO 尺寸  
ICON_SIZES = [16,24,32,48,64,96,128,192,256]  
CFG = configparser.ConfigParser()  
if getattr(sys, 'frozen', False):  
    base_dir = Path(sys.executable).parent  
else:  
    base_dir = Path(__file__).resolve().parent  
CFG_FILE = base_dir / "config.ini"  
LAST_DIR_KEY = "last_dir"  

# 加载或初始化配置  
if CFG_FILE.exists():  
    CFG.read(CFG_FILE, encoding="utf-8")  
else:  
    CFG["DEFAULT"] = {LAST_DIR_KEY: str(Path.home())}  
    with open(CFG_FILE, "w", encoding="utf-8") as f:  
        CFG.write(f)  

class App(tk.Tk):  
    def __init__(self):  
        super().__init__()  
        self.title("PNG/JPG → ICO 批量转换器")  
        self.resizable(False, False)  
        # 先读配置里的上次目录  
        self.last_dir = Path(CFG["DEFAULT"].get(LAST_DIR_KEY, str(Path.home())))  
        # 构建界面  
        self._build_ui()  
        # 默认在输入框里显示上次目录  
        self.path_var.set(str(self.last_dir))  

    def _build_ui(self):  
        fr = ttk.Frame(self, padding=10)  
        fr.grid()  
        ttk.Label(fr, text="文件或目录：").grid(row=0, column=0, sticky="w")  
        self.path_var = tk.StringVar()  
        ttk.Entry(fr, textvariable=self.path_var, width=50).grid(row=0, column=1, padx=5)  
        ttk.Button(fr, text="浏览…", command=self.on_browse).grid(row=0, column=2)  
        ttk.Button(fr, text="开始转换", command=self.on_convert).grid(row=1, column=0, columnspan=3, pady=10)  

    def on_browse(self):  
        cur = Path(self.path_var.get())  
        if cur.is_file():  
            d = cur.parent  
        elif cur.is_dir():  
            d = cur  
        else:  
            d = self.last_dir  
        file = filedialog.askopenfilename(title="选择 PNG/JPG", initialdir=str(d),  
            filetypes=[("Image","*.png;*.jpg;*.jpeg")])  
        if file:  
            self.path_var.set(file)  
            self.last_dir = Path(file).parent  
            CFG["DEFAULT"][LAST_DIR_KEY] = str(self.last_dir)  
            with open(CFG_FILE, "w", encoding="utf-8") as f:  
                CFG.write(f)  

    def on_convert(self):  
        p = Path(self.path_var.get().strip())  
        if not p.exists():  
            return messagebox.showerror("错误", "请输入有效的文件或目录路径！")  
        if p.is_file() and p.suffix.lower() in [".png",".jpg",".jpeg"]:  
            files = [p]  
        elif p.is_dir():  
            files = [f for f in p.iterdir() if f.suffix.lower() in [".png",".jpg",".jpeg"]]  
        else:  
            return messagebox.showerror("错误", "仅支持 PNG/JPG 文件或包含它们的目录！")  
        if not files:  
            return messagebox.showinfo("提示", "没有找到任何 PNG/JPG 文件。")  
        for img in files:  
            try:  
                im = Image.open(img).convert("RGBA")  
                ico = img.with_suffix(".ico")  
                im.save(ico, format="ICO", sizes=[(s,s) for s in ICON_SIZES])  
            except Exception as e:  
                messagebox.showerror("转换失败", f"{img.name}：{e}")  
                return  
        messagebox.showinfo("完成", f"成功转换 {len(files)} 个文件！")  

if __name__ == "__main__":  
    App().mainloop()