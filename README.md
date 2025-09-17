# StarResonanceAutoHunt

一个用于《星痕共鸣》的自动刷`神奇生物`辅助脚本，帮助玩家快速切换线路并自动开始战斗。

> 游戏内有一个广为流传的共识：**顺线或逆线刷神奇生物**，本脚本就是基于这个思路开发的。

---

## 🔧 功能简介

- 截图识别当前线路号（通过 OCR 图像识别）
- 支持使用键盘快捷键快速切线
- 自动发送 `H` 键进行战斗

⚠️ 注意：自动切线依靠[StarResonanceDamageCounter](https://github.com/dmlgzs/StarResonanceDamageCounter)服务>=v3.2。

---

## ⚙️ 启动参数说明

本程序支持以下命令行参数：

| 参数                 | 简写   | 类型         | 默认值   | 说明              |
| ------------------ | ---- | ---------- | ----- | --------------- |
| `--offset`         | `-o` | int        | `-1`  | 自动切线时的偏移量       |
| `--wait`           | `-w` | flag       | False | 是否等待（出现则为 True） |
| `--name <str...>`  | `-n` | list\[str] | `[]`  | 敌人名称（可接收多个）     |
| `--lines <int...>` | `-l` | list\[int] | `[]`  | 要处理的行号列表（可多个）   |


## 🎮 快捷键说明

| 键盘按键       | 功能描述           |
|----------------|--------------------|
| `+`          | 切到后一条线路并自动按 H 开始战斗 |
| `-`          | 切到前一条线路并自动按 H 开始战斗 |
| `~`          | 退出程序           |
| `.`          | 开启自动切线           |

---

## 🛠 使用前准备

1. **安装依赖**：

```bash
pip install -r requirements.txt
````

包括但不限于以下 Python 包：

* `easyocr`
* `pyautogui`
* `opencv-python`
* `keyboard`
* `numpy`

2. **Tesseract-OCR 无需安装**，使用的是 EasyOCR，更适合识别数字内容。

3. **确保游戏窗口在前台可见**，程序会截图并识别其内容。

### ⚠️ PyTorch 安装建议（重要）

`torch`（PyTorch）安装建议你根据你的系统和是否有 GPU 来选择合适的版本。

示例（CPU 版本）：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

如果你有 NVIDIA GPU 并希望使用 CUDA，请访问：
👉 [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

---

## 🚀 启动脚本

```bash
python main.py
```

运行后监听按键操作，按照快捷键说明进行控制。

---

## 📌 注意事项

* 使用前先按下 **P** 键打开频道界面
* 请确保使用的是管理员权限运行脚本（某些系统下才能正确监听按键）
* 识别不准时会保存截图以供排查

---

## 📷 效果演示（可选）

> 截图 / 动图放这里

---

## 📄 License

GNU GENERAL PUBLIC LICENSE Version 3

