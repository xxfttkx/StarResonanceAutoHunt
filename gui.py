import threading
import asyncio
import tkinter as tk
from tkinter import scrolledtext

from main import main  # 导入你的 main 函数


def start_asyncio_loop():
    asyncio.run(main())   # 调用你原来的 main()


def start_gui():
    root = tk.Tk()
    root.title("AutoHunt GUI")
    root.geometry("1920x1080")

    # 背景
    root.configure(bg="#f0f4f7")

    # ================= 左边区域 =================
    left_frame = tk.Frame(root, bg="#f0f4f7")
    left_frame.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)

    tk.Label(
        left_frame,
        text="选择目标敌人",
        font=("Microsoft YaHei", 16, "bold"),
        bg="#f0f4f7"
    ).pack(anchor="w", pady=10)

    enemy_names = ["小猪·闪闪", "娜宝·银辉", "娜宝·闪闪", "小猪·爱", "小猪·风"]

    check_vars = []
    for name in enemy_names:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(
            left_frame,
            text=name,
            variable=var,
            font=("Microsoft YaHei", 14),
            bg="#f0f4f7"
        )
        chk.pack(anchor="w", pady=5)
        check_vars.append(var)

    # 输入 lines 的地方
    tk.Label(
        left_frame,
        text="输入线路 (lines = [...])",
        font=("Microsoft YaHei", 14, "bold"),
        bg="#f0f4f7"
    ).pack(anchor="w", pady=15)

    lines_entry = tk.Text(left_frame, height=6, width=40, font=("Consolas", 12))
    lines_entry.pack(pady=5)

    # ================= 右边日志区域 =================
    right_frame = tk.Frame(root, bg="#ffffff")
    right_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    tk.Label(
        right_frame,
        text="运行日志",
        font=("Microsoft YaHei", 16, "bold"),
        bg="#ffffff"
    ).pack(anchor="w", pady=10)

    log_area = scrolledtext.ScrolledText(
        right_frame,
        wrap=tk.WORD,
        width=100,
        height=40,
        font=("Consolas", 12),
        bg="#1e1e1e",
        fg="#dcdcdc"
    )
    log_area.pack(fill="both", expand=True)

    # ================= 底部按钮 =================
    bottom_frame = tk.Frame(root, bg="#f0f4f7")
    bottom_frame.grid(row=1, column=0, columnspan=2, pady=20)

    start_btn = tk.Button(
        bottom_frame,
        text="▶ 启动",
        font=("Microsoft YaHei", 14),
        width=15,
        height=2,
        bg="#4CAF50",
        fg="white",
        relief="flat",
        command=lambda: threading.Thread(target=start_asyncio_loop, daemon=True).start()
    )
    start_btn.pack(side="left", padx=20)

    quit_btn = tk.Button(
        bottom_frame,
        text="✖ 退出",
        font=("Microsoft YaHei", 14),
        width=15,
        height=2,
        bg="#E53935",
        fg="white",
        relief="flat",
        command=root.quit
    )
    quit_btn.pack(side="left", padx=20)

    # 让左右两列自适应拉伸
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=2)

    root.mainloop()


if __name__ == '__main__':
    start_gui()
