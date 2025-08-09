# main.py
import ctypes
import time
ctypes.windll.shcore.SetProcessDpiAwareness(2) 
import torch
import game_logic
import sys
sys.stdout.reconfigure(encoding='utf-8')
import keyboard
from utils import *
from listener import listen, set_monster_alive_callback, set_not_monster_alive_callback
import asyncio

class AutoHuntController:
    def __init__(self, target_window):
        self.target_window = target_window
        self.auto_switch = False
        self.count = 0
        self.auto_switch_set = False

    def switch_line_and_h(self, offset):
        try:
            log(f"尝试切换线路，偏移量: {offset}")
            game_logic.switch_line(self.target_window, offset)
            game_logic.wait_and_press_h(self.target_window)
        except Exception as e:
            log(f"热键执行失败: {e}")

    def notify_monster_alive(self):
        self.count = 0

    def notify_not_monster_alive(self):
        if self.auto_switch and self.auto_switch_set:
            self.count += 1
            if self.count > 60:
                self.auto_switch = False
                self.count = 0
                log("3s没发现神奇动物，自动切线")
                game_logic.switch_line(self.target_window, -1)
                game_logic.wait_and_press_h(self.target_window)
                # game_logic.move_cursor(self.target_window)
                time.sleep(3)
                self.auto_switch = True
                self.count = 0
    
    def exit_program(self):
        log("检测到ESC键，退出程序")
        os._exit(0)

    def changeAutoSwitch(self):
        if self.auto_switch_set:
            self.auto_switch_set = False
            self.auto_switch = False
            self.count = 0
            log("自动切线已关闭")
        else:
            self.auto_switch_set = True
            self.auto_switch = True
            log("自动切线已开启")

async def main():
    target_window = find_target_window()
    if target_window is None:
        log("请先启动游戏")
        return
    controller = AutoHuntController(target_window)
    # screenshot_window(target_window)
    print("CUDA 是否可用：", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU 名称：", torch.cuda.get_device_name(0))

    # 注册事件回调
    set_monster_alive_callback(controller.notify_monster_alive)
    set_not_monster_alive_callback(controller.notify_not_monster_alive)

    # 绑定热键
    keyboard.add_hotkey('-', lambda: controller.switch_line_and_h(-1))
    keyboard.add_hotkey('+', lambda: controller.switch_line_and_h(1))
    keyboard.add_hotkey('/', controller.exit_program)
    keyboard.add_hotkey('.', controller.changeAutoSwitch)
    try:
        await listen()
    except Exception as e:
        log(f"监听过程中发生错误: {e}")
    keyboard.wait()  # 阻塞，持续监听热键事件

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
    
        
    