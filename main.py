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
from listener import EnemyListener
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
    parser.add_argument(
        "-l", "--lines",
        type=str_to_list,
        default=[],
        help="要处理的行号列表，如 '12 23 56-78'"
    )
    return parser.parse_args()

class AutoHuntController:
    def __init__(self):
        pass

    def init(self):
        target_window = find_target_window()
        # move_window_to_top_left(target_window)
        args = parse_args()
        self.initialize(target_window,args.offset,args.name,args.lines)

    def initialize(self,target_window,offset,enemy_names,lines):
        self.target_window = target_window
        self.auto_switch = False
        self.auto_switch_set = False
        self.lock = threading.Lock()  # 真锁
        self.logic_current_line = 0
        self.target_line = 0  # 目标线路编号
        self.offset = offset
        self.lines = lines
        if not self.lines:
            self.lines = offset < 0 and list(range(200, 0, -1)) or list(range(1, 201))
        self.delay = 0.5
        # self.target_group = ["小猪·闪闪","娜宝·银辉","娜宝·闪闪"]
        self.target_group = enemy_names if enemy_names else ["小猪·爱","小猪·风"]
        self.enemy_listener = None
    
    def cal_curr_line(self):
        if self.logic_current_line == 0:
            self.cal_curr_line_by_screenshot()
    
    def cal_curr_line_by_screenshot(self):
        self.logic_current_line = game_logic.get_curr_line(self.target_window)
        log(f"当前线路: {self.logic_current_line}")

    def cal_target_line(self, offset):
        self.cal_curr_line()
        lines = self.lines
        def get_next_line(lines, line):
            if line in lines:
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    return lines[idx + 1]
                else:
                    return -1
            return -1
        next_line = get_next_line(lines, self.logic_current_line)
        log(f"next_line {next_line}")
        if next_line != -1:
            self.target_line = next_line
            return None
        self.target_line = self.logic_current_line + offset
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
            self.logic_current_line = self.target_line
        except Exception as e:
            log(f"热键执行失败: {e}")

    def _switch_line_job(self):
        self.auto_switch = False
        self.switch_line_and_h(self.offset)  # 切换到下一条线
        self.auto_switch = True
    
    def notify_monster_dead(self):
        if not self.lock.acquire(blocking=False):
            return
        try:
            if self.auto_switch and self.auto_switch_set:
                if self.delay and self.delay > 0:
                    log(f"等待 {self.delay} 秒后切线")
                    time.sleep(self.delay)
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
            log("自动切线已关闭")
            self.logic_current_line = 0
        else:
            self.auto_switch_set = True
            self.auto_switch = True
            log("自动切线已开启")
    
    def set_enemy_target(self, name, selected):
        if selected and name not in self.target_group:
            self.target_group.append(name)
        if not selected and name in self.target_group:
            self.target_group.remove(name)
        self.enemy_listener.set_target_group(self.target_group)
    
    def set_enemy_group(self, enemy_names):
        self.target_group = enemy_names
        self.enemy_listener.set_target_group(self.target_group)
            
    
    def set_lines(self, lines):
        self.lines = str_to_list(lines)
        log(f"设置监听线路为: {self.lines}")
        
    async def startAutoHunt(self):
        log(f"监听的怪物名称: {self.target_group}")
        log(f"监听的线路: {self.lines}")
        # screenshot_window(target_window)
        log(f"CUDA 是否可用：{torch.cuda.is_available()}")
        if torch.cuda.is_available():
            log(f"GPU 名称：{torch.cuda.get_device_name(0)}")
        keyboard.add_hotkey('/', self.exit_program)
        keyboard.add_hotkey('.', self.changeAutoSwitch)
        self.enemy_listener = EnemyListener(self.target_group)
        self.enemy_listener.set_monster_dead_callback(self.notify_monster_dead)
        while True:
            try:
                log("开始监听...")
                await self.enemy_listener.listen()
            except Exception as e:
                log(f"监听过程中发生错误: {e}")
                time.sleep(10)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    controller = AutoHuntController()
    controller.init()
    asyncio.run(controller.startAutoHunt())