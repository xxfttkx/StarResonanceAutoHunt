import keyboard
from utils import *
import pyautogui
import time
import easyocr
import re
from PIL import Image
    
def get_curr_line(win):
    # 获取客户区屏幕坐标
    x1, y1, x2, y2 = get_client_rect(win)

    # 手动设定线路显示区域的 ROI（相对于客户区）
    rect = (189, 236, 218, 252)  # ltrb — 你需要自己测定
    rect_all = (42,236,251,252)
    rect = get_scale_area(rect, *get_window_width_and_height(win))
    rect = ltrb_add_win(rect, win)  # 将窗口位置添加到矩形中
    # screenshot_window(win)  # 截图窗口以便后续处理
    # 截图
    screenshot = capture_roi(*ltrb_to_xywh(*rect))
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
    cv2.imwrite("output_binary.png", binary)

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
        image = Image.fromarray(np_image)
        save_screenshot(image)  # 保存截图以便调试
        return None
        


def switch_line(win, line):
    """激活窗口并切换线路"""
    try:
        if not win.isActive:
            win.activate()
            time.sleep(0.5)  # 稍等窗口激活

        # 按下切线快捷键 p
        pyautogui.press('p')
        time.sleep(1)  # 等待切线面板弹出

        # 点击线路输入框（根据实际位置修改）
        input_box_pos = (1492,1007)  # 示例为屏幕中心，请替换为实际坐标
        input_box_pos = get_scale_point(input_box_pos, *get_window_width_and_height(win))
        input_box_pos = point_add_win()
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
        color = get_pixel_color(px, py)
        if not is_black(color):
            break

        if time.time() - start_time > timeout:
            log("等待超时，强制继续")
            break

        time.sleep(2)

    log("切线结束，发送战斗按键 H")
    keyboard.press_and_release('h')