import sys
import tkinter as tk
from tkinter import scrolledtext

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, s):
        # 在 Tk 主线程里安全更新
        self.widget.after(0, self._append, s)

    def _append(self, s):
        self.widget.insert(tk.END, s, (self.tag,))
        self.widget.see(tk.END)  # 自动滚动到底部

    def flush(self):  # 兼容 file-like 对象
        pass
