import keyboard
from utils import *
import pyautogui
import time
import easyocr
import re
from PIL import Image
    
def get_curr_line(win):
    # 获取客户区屏幕坐标

    # 手动设定线路显示区域的 ROI（相对于客户区）
    rect = (1479,97,1554,127)
    line = None
    rect = get_scale_area(rect, *get_window_width_and_height(win))
    rect = ltrb_add_win(rect, win)  # 将窗口位置添加到矩形中
    line = ltrb_to_num(rect)
    if not line:
        log('未能从切换频道窗口识别出线路号，尝试识别左上线路号')
        rect_all = (42,236,251,252)
        rect = get_scale_area(rect_all, *get_window_width_and_height(win))
        rect = ltrb_add_win(rect, win)  # 将窗 口位置添加到矩形中
        line = ltrb_to_num(rect)
    
    while line>200:
        line-=100

    if line:
        log(f"当前线路识别结果: {line}")
        return line
    else:
        return None
        


def switch_line(win, line):
    """激活窗口并切换线路"""
    try:
        if not win.isActive:
            win.activate()
            time.sleep(0.2)  # 稍等窗口激活
    except Exception as e:
        log(f"activate_win failed:{e}")

    try:
        # # 按下切线快捷键 p
        # pyautogui.press('p')
        # time.sleep(0.5)  # 等待切线面板弹出
        
        # 点击线路输入框（根据实际位置修改）
        input_box_pos = (1492,1007)  # 示例为屏幕中心，请替换为实际坐标
        input_box_pos = get_scale_point(input_box_pos, *get_window_width_and_height(win))
        input_box_pos = point_add_win(input_box_pos, win)  # 将窗口位置添加到点击位置
        pyautogui.click(input_box_pos)
        time.sleep(0.2)

        # 输入线路号
        pyautogui.typewrite(str(line), interval=0.05)

        # 按回车确认
        pyautogui.press('enter')
        log(f"已切换到线路 {line}")

    except Exception as e:
        log(f"switch_line failed:{e}")

def wait_and_press_h(win):
    time.sleep(5)
    log("等待切线完成（黑屏结束）...")

    x1, y1, x2, y2 = get_client_rect(win)
    width = x2 - x1
    height = y2 - y1

    # 监测点位置（客户区下方90%高度处中间）
    px = x1 + width // 2
    py = y1 + int(height * 0.90)

    def is_black(rgb, threshold=30):
        # 判断是否接近黑色（R/G/B 都低于阈值）
        return all(channel < threshold for channel in rgb)

    timeout = 14  # 最多等待 14 秒
    start_time = time.time()

    while True:
        color = get_pixel_color(px, py)
        if not is_black(color):
            break

        if time.time() - start_time > timeout:
            log("等待超时，强制继续")
            break

        time.sleep(2)

    log("切线结束，发送战斗按键 H")
    keyboard.press_and_release('h')
    time.sleep(0.3)
    keyboard.press_and_release('esc')
    time.sleep(0.3)
    keyboard.press_and_release('p')

def move_cursor(win):
    try:
        if not win.isActive:
            win.activate()
            time.sleep(0.2)  # 稍等窗口激活
    except Exception as e:
        log(f"activate_win failed:{e}")
    # 每次右移 2 像素，移动 50 次
    move_mouse()
