# main.py
import ctypes
import game_logic
ctypes.windll.shcore.SetProcessDpiAwareness(2) 
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import keyboard
from utils import *


if __name__ == "__main__":
    target_window = find_target_window()
    if target_window is None:
        log("请先启动游戏")
        exit(1)
    move_window_to_top_left(target_window)
    while True:
        if keyboard.is_pressed('esc'):
            log("检测到ESC键，退出程序")
            break
        if keyboard.is_pressed('num 2'):
            log("检测到num 2键, line = line - 1")
            line = game_logic.get_curr_line(target_window)
            if line is None:
                log("无法获取当前线路，请检查游戏窗口")
                continue
            game_logic.switch_line(target_window, line - 1)
            game_logic.wait_and_press_h(target_window)
        if keyboard.is_pressed('num 3'):
            log("检测到num 2键, line = line + 1")
            line = game_logic.get_curr_line(target_window)
            if line is None:
                log("无法获取当前线路，请检查游戏窗口")
                continue
            game_logic.switch_line(target_window, line + 1)
            game_logic.wait_and_press_h(target_window)
        time.sleep(0.1)
    