# main.py
import ctypes
import torch
import game_logic
ctypes.windll.shcore.SetProcessDpiAwareness(2) 
import sys
sys.stdout.reconfigure(encoding='utf-8')
import keyboard
from utils import *

def switch_line_and_h(target_window, offset):
    log(f"尝试切换线路，偏移量: {offset}")
    line = game_logic.get_curr_line(target_window)
    if line is None:
        log("无法获取当前线路，请检查游戏窗口")
        return
    game_logic.switch_line(target_window, line + offset)
    game_logic.wait_and_press_h(target_window)

def exit_program():
    log("检测到ESC键，退出程序")
    os._exit(0)  # 强制退出整个程序

if __name__ == "__main__":
    target_window = find_target_window()
    if target_window is None:
        log("请先启动游戏")
        exit(1)
    # screenshot_window(target_window)  # 保存初始截图以便调试
    # move_window_to_top_left(target_window)
    print("CUDA 是否可用：", torch.cuda.is_available())
    print("GPU 名称：", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "无")
    keyboard.add_hotkey('-', lambda: switch_line_and_h(target_window,-1))
    keyboard.add_hotkey('+', lambda: switch_line_and_h(target_window,1))
    keyboard.add_hotkey('~', exit_program)
    keyboard.wait()  # 阻塞，持续监听热键事件
    