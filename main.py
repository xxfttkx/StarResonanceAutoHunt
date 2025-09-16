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
from listener import listen, set_monster_alive_callback, set_not_monster_alive_callback, set_monster_dead_callback
import asyncio
import threading
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--offset",        # 同时支持 -o 和 --offset
        type=int,
        default=-1,
        help="自动切线时的偏移量"
    )
    parser.add_argument(
        "-w", "--wait",
        action="store_true",   # 出现时为 True，不出现时为 False
        help="是否等待"
    )
    parser.add_argument(
        "-n", "--name",
        type=str,
        nargs="+",          # 接收一个或多个
        default=[],
        help="hunt enemy name(s)"
    )
    return parser.parse_args()

class AutoHuntController:
    def __init__(self, target_window, offset=-1):
        self.target_window = target_window
        self.auto_switch = False
        self.count = 0
        self.auto_switch_set = False
        self.lock = threading.Lock()  # 真锁
        self.target_line = 0  # 目标线路编号
        self.offset = offset
    
    def get_curr_line(self):
        if self.target_line==0:
            return game_logic.get_curr_line(self.target_window)
        else:
            return self.target_line

    def cal_target_line(self, offset):
        
        logic_current_line = self.get_curr_line()
        lines = [200, 199, 198, 194, 193, 192, 190, 188, 186, 185, 184, 182, 181, 
            177, 176, 175, 174, 173, 171, 169, 168, 167, 165, 164, 163, 160, 
            158, 157, 155, 154, 152, 151, 150, 149, 147, 146, 145, 144, 143, 
            141, 140, 139, 138, 137, 134, 133, 131, 129, 128, 127, 126, 125, 
            123, 122, 121, 118, 115, 114, 112, 111, 110, 109, 107, 106, 105, 
            104, 102, 101, 98, 97, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 
            84, 83, 81, 79, 77, 76, 75, 73, 71, 70]
        
        lines = [7,11,19,23,25,30,32,39,46,59,68,71,88,92,118,122]


        def get_next_line(lines, line):
            if line in lines:
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    return lines[idx + 1]
                else:
                    return -1
            return -1
        if not lines:
            log("所有线都存在")
        else:
            next_line = get_next_line(lines, logic_current_line)
            log(f"next_line {next_line}")
            if next_line != -1:
                self.target_line = next_line
                return None

        self.target_line = logic_current_line + offset
        # 线路数越界
        if self.target_line > 200:
            self.target_line = 1
        if self.target_line < 1:
            self.target_line = 200
        return self.target_line

    def switch_line_and_h(self, offset):
        try:
            log(f"尝试切换线路，偏移量: {offset}")
            self.cal_target_line(offset)
            game_logic.switch_line(self.target_window, self.target_line)
            game_logic.wait_and_press_h(self.target_window)
        except Exception as e:
            log(f"热键执行失败: {e}")

    def notify_monster_alive(self):
        self.count = 0

    def _switch_line_job(self):
        self.auto_switch = False
        self.count = 0
        self.switch_line_and_h(self.offset)  # 切换到下一条线
        self.auto_switch = True
        self.count = 0

    def notify_not_monster_alive(self):
        # 尝试获取锁，如果拿不到锁说明有任务在执行，直接跳过
        if not self.lock.acquire(blocking=False):
            return
        try:
            if self.auto_switch and self.auto_switch_set:
                self.count += 1
                over_time = 2
                if self.count > over_time:
                    log(f"{over_time}s没发现神奇动物，自动切线")
                    threading.Thread(target=self._switch_line_job).start()
        finally:
            self.lock.release()
    
    def notify_monster_dead(self):
        if not self.lock.acquire(blocking=False):
            return
        try:
            if self.auto_switch and self.auto_switch_set:
                threading.Thread(target=self._switch_line_job).start()
        finally:
            self.lock.release()
    
    def exit_program(self):
        log("检测到 / 键，退出程序")
        os._exit(0)

    def changeAutoSwitch(self):
        self.target_line = 0
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
    args = parse_args()
    offset = args.offset
    enemy_names = args.name
    while target_window is None:
        log("请先启动游戏")
        time.sleep(10)
        target_window = find_target_window()
    controller = AutoHuntController(target_window, offset)
    # screenshot_window(target_window)
    print("CUDA 是否可用：", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU 名称：", torch.cuda.get_device_name(0))

    # 注册事件回调
    set_monster_alive_callback(controller.notify_monster_alive)
    set_not_monster_alive_callback(controller.notify_not_monster_alive)
    set_monster_dead_callback(controller.notify_monster_dead)  # 死亡事件直接切线

    offset = abs(offset)  # 确保偏移量为正数
    # 绑定热键
    # keyboard.add_hotkey('-', lambda: controller.switch_line_and_h(-offset))
    # keyboard.add_hotkey('+', lambda: controller.switch_line_and_h(offset))
    keyboard.add_hotkey('/', controller.exit_program)
    keyboard.add_hotkey('.', controller.changeAutoSwitch)
    while True:
        try:
            await listen(enemy_names)
        except Exception as e:
            log(f"监听过程中发生错误: {e}")
            time.sleep(10)
            
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
    
        
    
