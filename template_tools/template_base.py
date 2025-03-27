import cv2
import numpy as np
import pyautogui
import time
import os
import sys

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """打印程序标题"""
    print("="*50)
    print(title.center(48))
    print("="*50)
    print()

def create_template_directory():
    """创建模板目录"""
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"已创建模板目录: {templates_dir}")
    else:
        print(f"模板目录已存在: {templates_dir}")
    return templates_dir

def check_existing_templates(templates_dir, required_templates):
    """检查已存在的模板"""
    existing_templates = []
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            existing_templates.append(template)
        else:
            missing_templates.append(template)
    
    return existing_templates, missing_templates

def capture_template(template_name, templates_dir):
    """捕获模板图像"""
    print(f"\n准备捕获模板: {template_name}")
    print("请将鼠标移动到要截图的区域左上角，然后按Enter")
    input()
    start_x, start_y = pyautogui.position()
    
    print("现在将鼠标移动到区域右下角，然后按Enter")
    input()
    end_x, end_y = pyautogui.position()
    
    width = end_x - start_x
    height = end_y - start_y
    
    if width <= 0 or height <= 0:
        print("错误: 选择的区域无效，宽度和高度必须大于0")
        return False
    
    print(f"选择的区域: ({start_x}, {start_y}, {width}, {height})")
    
    # 捕获屏幕区域
    screenshot = pyautogui.screenshot(region=(start_x, start_y, width, height))
    template_path = os.path.join(templates_dir, template_name)
    screenshot.save(template_path)
    
    print(f"已保存模板: {template_path}")
    
    # 显示捕获的模板
    template_img = cv2.imread(template_path)
    if template_img is not None:
        # 调整图像大小以便于查看
        scale = min(1.0, 400 / max(width, height))
        display_width = int(width * scale)
        display_height = int(height * scale)
        display_img = cv2.resize(template_img, (display_width, display_height))
        
        cv2.imshow(f"模板: {template_name}", display_img)
        cv2.waitKey(1500)  # 显示1.5秒
        cv2.destroyAllWindows()
    
    return True