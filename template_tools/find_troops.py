# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pyautogui
import time
import os
import sys
import random

# 使用绝对导入替代相对导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from autogame import AutoGame
from template_tools.template_base import clear_screen, print_header, create_template_directory, check_existing_templates, capture_template

def find_troops_main():
    """
    主函数：自动拖动地图寻找野怪部队
    """
    clear_screen()
    print_header("三国志战略版 - 自动寻找野怪部队工具")
    
    # 创建模板目录
    templates_dir = create_template_directory()
    
    # 检查必要的模板是否存在
    required_templates = [
        'troop_level1.png',  # 1级野怪
        'troop_level2.png',  # 2级野怪
        'troop_level3.png',  # 3级野怪
        'troop_level4.png',  # 4级野怪
        'troop_level5.png',  # 5级野怪
    ]
    
    existing_templates, missing_templates = check_existing_templates(templates_dir, required_templates)
    
    if missing_templates:
        print("\n缺少以下野怪模板图像:")
        for template in missing_templates:
            print("  - {0}".format(template))
        
        print("\n是否现在创建这些模板? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            create_troop_templates(missing_templates, templates_dir)
        else:
            print("请先创建必要的模板图像再使用此功能")
            return
    
    # 创建AutoGame实例
    auto_game = AutoGame(confidence=0.7)
    
    # 开始寻找野怪
    print("\n准备开始寻找野怪...")
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        time.sleep(1)
    
    # 询问用户要寻找的野怪等级
    print("\n请选择要寻找的野怪等级:")
    print("1. 1级野怪")
    print("2. 2级野怪")
    print("3. 3级野怪")
    print("4. 4级野怪")
    print("5. 5级野怪")
    print("0. 所有等级")
    
    level_choice = input("请输入选项编号: ").strip()
    
    if level_choice == '0':
        target_templates = [f'troop_level{i}.png' for i in range(1, 6)]
    elif level_choice in ['1', '2', '3', '4', '5']:
        target_templates = [f'troop_level{level_choice}.png']
    else:
        print("无效的选择，默认寻找所有等级野怪")
        target_templates = [f'troop_level{i}.png' for i in range(1, 6)]
    
    # 询问搜索方向
    print("\n请选择地图拖动方向:")
    print("1. 向上拖动 (地图向下移动)")
    print("2. 向下拖动 (地图向上移动)")
    print("3. 向左拖动 (地图向右移动)")
    print("4. 向右拖动 (地图向左移动)")
    print("5. 螺旋形搜索 (从中心向外)")
    
    direction_choice = input("请输入选项编号: ").strip()
    
    # 开始搜索
    try:
        if direction_choice == '5':
            found = spiral_search(auto_game, target_templates, max_iterations=50)
        else:
            directions = {
                '1': 'up',
                '2': 'down',
                '3': 'left',
                '4': 'right'
            }
            direction = directions.get(direction_choice, 'right')  # 默认向右拖动
            found = directional_search(auto_game, target_templates, direction, max_iterations=50)
        
        if found:
            print("\n成功找到目标野怪!")
            # 播放提示音
            for _ in range(3):
                print('\a')  # 系统提示音
                time.sleep(0.5)
        else:
            print("\n未找到目标野怪，已达到最大搜索次数")
    
    except KeyboardInterrupt:
        print("\n搜索已被用户中断")
    
    print("\n程序结束，按Enter键退出...")
    input()

def create_troop_templates(missing_templates, templates_dir):
    """
    创建野怪模板图像
    """
    print("\n开始创建野怪模板图像...")
    print("请在游戏中找到对应等级的野怪，然后按照提示进行操作")
    
    print("\n请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    for template in missing_templates:
        print(f"\n准备创建模板: {template}")
        print(f"请找到一个{template.replace('troop_level', '').replace('.png', '')}级野怪")
        capture_template(template, templates_dir)
        
        print("是否继续创建下一个模板? (y/n)")
        choice = input().strip().lower()
        if choice != 'y':
            break

def directional_search(auto_game, target_templates, direction, max_iterations=50):
    """
    按指定方向拖动地图搜索野怪
    """
    print(f"\n开始向{direction}方向搜索野怪...")
    print("按Ctrl+C可随时中断搜索")
    
    # 设置拖动参数
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # 拖动距离和方向
    drag_distance = 300  # 每次拖动的像素距离
    
    if direction == 'up':
        start_x, start_y = center_x, center_y - drag_distance//2
        end_x, end_y = center_x, center_y + drag_distance//2
    elif direction == 'down':
        start_x, start_y = center_x, center_y + drag_distance//2
        end_x, end_y = center_x, center_y - drag_distance//2
    elif direction == 'left':
        start_x, start_y = center_x - drag_distance//2, center_y
        end_x, end_y = center_x + drag_distance//2, center_y
    else:  # right
        start_x, start_y = center_x + drag_distance//2, center_y
        end_x, end_y = center_x - drag_distance//2, center_y
    
    for iteration in range(1, max_iterations + 1):
        print(f"搜索次数: {iteration}/{max_iterations}")
        
        # 检查当前屏幕是否有目标
        for template in target_templates:
            position = auto_game.find_template(template, confidence=0.7)
            if position:
                print(f"找到目标: {template} 在位置 {position}")
                # 点击目标
                auto_game.click(position)
                return True
        
        # 拖动地图
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=0.5)  # 0.5秒完成拖动
        pyautogui.mouseUp()
        
        # 等待地图停止移动
        time.sleep(1)
    
    return False

def spiral_search(auto_game, target_templates, max_iterations=50):
    """
    螺旋形搜索野怪
    """
    print("\n开始螺旋形搜索野怪...")
    print("按Ctrl+C可随时中断搜索")
    
    # 设置拖动参数
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # 螺旋搜索参数
    directions = ['right', 'down', 'left', 'up']  # 右、下、左、上
    direction_index = 0
    steps_per_side = 1  # 每个方向拖动的次数
    steps_taken = 0
    side_changes = 0
    
    drag_distance = 300  # 每次拖动的像素距离
    
    for iteration in range(1, max_iterations + 1):
        print(f"搜索次数: {iteration}/{max_iterations}")
        
        # 检查当前屏幕是否有目标
        for template in target_templates:
            position = auto_game.find_template(template, confidence=0.7)
            if position:
                print(f"找到目标: {template} 在位置 {position}")
                # 点击目标
                auto_game.click(position)
                return True
        
        # 确定当前拖动方向
        current_direction = directions[direction_index]
        
        # 设置拖动起点和终点
        if current_direction == 'right':
            start_x, start_y = center_x - drag_distance//2, center_y
            end_x, end_y = center_x + drag_distance//2, center_y
        elif current_direction == 'down':
            start_x, start_y = center_x, center_y - drag_distance//2
            end_x, end_y = center_x, center_y + drag_distance//2
        elif current_direction == 'left':
            start_x, start_y = center_x + drag_distance//2, center_y
            end_x, end_y = center_x - drag_distance//2, center_y
        else:  # up
            start_x, start_y = center_x, center_y + drag_distance//2
            end_x, end_y = center_x, center_y - drag_distance//2
        
        # 拖动地图
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=0.5)  # 0.5秒完成拖动
        pyautogui.mouseUp()
        
        # 等待地图停止移动
        time.sleep(1)
        
        # 更新螺旋搜索状态
        steps_taken += 1
        if steps_taken == steps_per_side:
            direction_index = (direction_index + 1) % 4
            steps_taken = 0
            side_changes += 1
            if side_changes == 2:
                steps_per_side += 1
                side_changes = 0
    
    return False

if __name__ == "__main__":
    find_troops_main()