
import os
import keyboard
from utils import *
import pyautogui
import pygetwindow as gw
import time
import pytesseract
from PIL import Image
import easyocr
import re
    
def get_curr_line(win):
    # 获取客户区屏幕坐标
    x1, y1, x2, y2 = get_client_rect(win)

    # 手动设定线路显示区域的 ROI（相对于客户区）
    rect = (189, 236, 218, 252)  # x, y, w, h — 你需要自己测定
    rect = get_scale_area(rect, *get_window_width_and_height(win))
    roi_x = x1 + rect[0]
    roi_y = y1 + rect[1]
    roi_w = rect[2] - rect[0]
    roi_h = rect[3] - rect[1]
    # screenshot_window(win)  # 截图窗口以便后续处理
    # 截图
    screenshot = pyautogui.screenshot(region=(roi_x, roi_y, roi_w, roi_h))
    np_image = np.array(screenshot)
    # ✅ 转为灰度图
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)

    # ✅ 自适应阈值二值化（提升对比度，适应复杂背景）
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    reader = easyocr.Reader(['en'], gpu=True)  # 只识别英文和数字
    results = reader.readtext(binary)
    # cv2.imwrite("output_binary.png", binary)

    digits = []

    for (_, text, prob) in results:
        log(f"识别结果: {text}, 置信度: {prob:.2f}")
        if prob > 0.5:  # 过滤低置信度的结果
            nums = re.findall(r'\d+', text)
            digits.extend(nums)

    if digits:
        line = int(''.join(digits))
        log(f"当前线路识别结果: {line}")
        return line
    else:
        log("未识别到纯数字")
        save_screenshot(screenshot)  # 保存截图以便调试
        return None
        


def switch_line(win, line):
    """激活窗口并切换线路"""
    try:
        if not win.isActive:
            win.activate()
            time.sleep(0.5)  # 稍等窗口激活

        # 按下切线快捷键 p
        pyautogui.press('p')
        time.sleep(0.5)  # 等待切线面板弹出

        # 点击线路输入框（根据实际位置修改）
        input_box_pos = (1492,1007)  # 示例为屏幕中心，请替换为实际坐标
        input_box_pos = get_scale_point(input_box_pos, *get_window_width_and_height(win))
        pyautogui.click(input_box_pos)
        time.sleep(0.2)

        # 输入线路号
        pyautogui.typewrite(str(line), interval=0.05)

        # 按回车确认
        pyautogui.press('enter')
        log(f"已切换到线路 {line}")

    except IndexError:
        log(f"switch_line failed")

def wait_and_press_h(win):
    time.sleep(2)
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

    timeout = 20  # 最多等待 20 秒
    start_time = time.time()

    while True:
        color = pyautogui.screenshot().getpixel((px, py))
        if not is_black(color):
            break

        if time.time() - start_time > timeout:
            log("等待超时，强制继续")
            break

        time.sleep(2)

    log("切线结束，发送战斗按键 H")
    keyboard.press_and_release('h')