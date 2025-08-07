from datetime import datetime
import os
import re
from PIL import Image
import cv2
import easyocr
import numpy as np
import pyautogui
import pygetwindow as gw
import win32gui
import win32con
import mss

def log(msg):
    """带时间前缀的打印函数"""
    now = datetime.now().strftime("[%H:%M:%S]")
    print(f"{now} {msg}")

def move_window_to_top_left(win):
    hwnd = win._hWnd  # 获取窗口句柄
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,  # 放在 Z 顺序的顶部
        0, 0,               # x=0, y=0
        0, 0,               # 宽高为 0（会被忽略）
        win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW  # 不改变大小，只移动并显示
    )

def find_target_window():
    """查找并返回窗口标题完全是 '星痕共鸣' 的窗口对象"""
    all_windows = gw.getAllWindows()
    for w in all_windows:
        if w.title == "星痕共鸣":
            log("成功获取目标窗口")
            return w
    log("未找到游戏窗口")
    return None

def get_client_rect(win):
    hwnd = win._hWnd  # 获取窗口句柄
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    # 转换为屏幕坐标（客户区左上、右下的屏幕绝对坐标）
    left_top = win32gui.ClientToScreen(hwnd, (left, top))
    right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])

def ltrb_add_win(rect, win):
    """将窗口位置添加到给定的 (left, top, right, bottom) 矩形"""
    left, top, right, bottom = rect
    # 获取窗口在屏幕上的位置
    win_left, win_top = get_client_rect(win)[:2]  # 获取窗口客户区左上角坐标
    return (left + win_left, top + win_top, right + win_left, bottom + win_top)

def point_add_win(point, win):
    """将窗口位置添加到给定的 (x, y) 点"""
    x, y = point
    # 获取窗口在屏幕上的位置
    win_left, win_top = get_client_rect(win)[:2]  # 获取窗口客户区左上角坐标
    return (x + win_left, y + win_top)

def get_window_width_and_height(win):
    """获取窗口的宽高"""
    hwnd = win._hWnd  # 获取窗口句柄
    rect = win32gui.GetClientRect(hwnd)
    return (rect[2] - rect[0]), (rect[3] - rect[1])

def get_pixel_color(x, y):
    with mss.mss() as sct:
        # 截取 x, y 处 1x1 的区域
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        sct_img = sct.grab(monitor)

        # 获取图像像素的 RGB 值（注意：sct_img是BGRA）
        pixel = sct_img.pixel(0, 0)  # (B, G, R, A)
        r, g, b = pixel[2], pixel[1], pixel[0]  # 转换为 RGB
        return (r, g, b)
    
def capture_roi(x,y, w, h):
    """截取指定区域的屏幕截图"""
    try:
        with mss.mss() as sct:
            monitor = {"left": x, "top": y, "width": w, "height": h}
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)# [:, :, :3]  # 去掉 alpha 通道
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    except Exception as e:
        log(f"截图失败: {e}")
        return None

def get_scale_area(rect, cur_w, cur_h, base_w=1920, base_h=1080):
    x1, y1, x2, y2 = rect
    scale_x = cur_w / base_w
    scale_y = cur_h / base_h
    return (
        int(x1 * scale_x),
        int(y1 * scale_y),
        int(x2 * scale_x),
        int(y2 * scale_y)
    )

def get_scale_point(point, cur_w, cur_h, base_w=1920, base_h=1080):
    x, y = point
    scale_x = cur_w / base_w
    scale_y = cur_h / base_h
    return int(x * scale_x), int(y * scale_y)

def save_screenshot(screenshot):
    # 创建失败截图保存文件夹（如不存在）
    save_fail_dir = 'screenshots'
    os.makedirs(save_fail_dir, exist_ok=True)

    # 用时间戳命名文件，防止覆盖
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_fail_dir, f"unrecognized_{timestamp}.png")

    # 保存截图
    screenshot.save(filename)
    print(f"已保存未识别截图到: {filename}")

def screenshot_window(win):
    """截取指定窗口的客户区"""
    try:
        x1, y1, x2, y2 = get_client_rect(win)
        width = x2 - x1
        height = y2 - y1
        screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
        save_screenshot(screenshot)  # 保存截图到指定目录
        return screenshot
    except Exception as e:
        log(f"截图失败: {e}")
        return None

def xywh_to_ltrb(x, y, w, h):
    """将 (x, y, w, h) 转换为 (left, top, right, bottom)"""
    return (x, y, x + w, y + h)

def ltrb_to_xywh(left, top, right, bottom):
    """将 (left, top, right, bottom) 转换为 (x, y, w, h)"""
    return (left, top, right - left, bottom - top)

def ltrb_to_num(rect):
    screenshot = capture_roi(*ltrb_to_xywh(*rect))
    np_image = np.array(screenshot)
    # ✅ 转为灰度图
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)

    # ✅ 自适应阈值二值化（提升对比度，适应复杂背景）
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)  # 只识别英文和数字
    results = reader.readtext(binary)
    cv2.imwrite("output_binary.png", binary)

    longest_num = None
    for (_, text, prob) in results:
        log(f"识别结果: {text}, 置信度: {prob:.2f}")
        nums = re.findall(r'\d+', text)
        longest_num = max(nums, key=len) if nums else None
            

    if longest_num:
        return int(longest_num)
    else:
        log("未识别到数字")
        image = Image.fromarray(np_image)
        save_screenshot(image)  # 保存截图以便调试