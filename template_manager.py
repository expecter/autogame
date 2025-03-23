import cv2
import numpy as np
import pyautogui
import time
import os
import sys
from autogame import AutoGame
from clash_royale_bot import ClashRoyaleBot

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    print("="*50)
    print("模板管理与测试工具".center(48))
    print("="*50)
    print()

def create_template_directory():
    """创建模板目录"""
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"已创建模板目录: {templates_dir}")
    else:
        print(f"模板目录已存在: {templates_dir}")
    return templates_dir

def list_required_templates():
    """列出所需的模板"""
    required_templates = [
        'battle_button.png',  # 主界面的对战按钮
        'confirm_battle.png',  # 确认开始战斗的按钮
        'victory_screen.png',  # 胜利画面
        'defeat_screen.png',  # 失败画面
        'ok_button.png',  # 确认按钮
        'card_slot_1.png',  # 卡牌槽位1
        'card_slot_2.png',  # 卡牌槽位2
        'card_slot_3.png',  # 卡牌槽位3
        'card_slot_4.png',  # 卡牌槽位4
    ]
    return required_templates

def check_existing_templates(templates_dir):
    """检查已存在的模板"""
    required_templates = list_required_templates()
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

def test_template(template_name, templates_dir, confidence=0.7):
    """测试模板识别"""
    print(f"\n测试模板: {template_name} (置信度: {confidence})")
    
    # 创建AutoGame实例用于测试
    auto_game = AutoGame(confidence=confidence)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 尝试识别模板
    position = auto_game.find_template(template_name, confidence=confidence)
    
    if position:
        print(f"成功识别模板 {template_name} 在位置 {position} (置信度: {confidence})")
        # 高亮显示识别区域
        screen = auto_game.take_screenshot()
        template_path = os.path.join(templates_dir, template_name)
        template = cv2.imread(template_path)
        h, w = template.shape[:2]
        
        # 在屏幕截图上绘制矩形标记识别区域
        cv2.rectangle(screen, (position[0]-w//2, position[1]-h//2), 
                     (position[0]+w//2, position[1]+h//2), (0, 255, 0), 2)
        
        # 显示标记后的屏幕截图
        scale = min(1.0, 800 / max(screen.shape[1], screen.shape[0]))
        display_width = int(screen.shape[1] * scale)
        display_height = int(screen.shape[0] * scale)
        display_img = cv2.resize(screen, (display_width, display_height))
        
        cv2.imshow("模板识别结果", display_img)
        cv2.waitKey(2000)  # 显示2秒
        cv2.destroyAllWindows()
        
        return True
    else:
        print(f"无法识别模板 {template_name}，请尝试重新捕获或调整置信度")
        return False

def test_battle_state_detection():
    """测试战斗状态检测"""
    print("\n测试战斗状态检测功能...")
    print("这将检查detect_battle_state函数是否能正确识别游戏状态")
    
    # 创建机器人实例
    bot = ClashRoyaleBot(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 检测战斗状态
    state = bot.detect_battle_state()
    print(f"检测到的战斗状态: {state}")
    
    # 根据状态提供建议
    if state == "main_menu":
        print("当前在主菜单，可以开始战斗")
        print("是否尝试点击对战按钮? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            if bot.click_template('battle_button.png'):
                print("已点击对战按钮")
                time.sleep(1)
                print("是否尝试点击确认对战按钮? (y/n)")
                choice = input().strip().lower()
                if choice == 'y':
                    if bot.click_template('confirm_battle.png'):
                        print("已点击确认对战按钮，等待进入战斗...")
                    else:
                        print("无法找到确认对战按钮，请检查confirm_battle.png模板")
            else:
                print("无法找到对战按钮，请检查battle_button.png模板")
    elif state == "in_battle":
        print("当前已在战斗中，可以执行战斗操作")
    elif state == "victory" or state == "defeat":
        print(f"战斗已结束，结果: {state}")
        print("是否尝试点击确认按钮? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            if bot.click_template('ok_button.png'):
                print("已点击确认按钮")
            else:
                print("无法找到确认按钮，请检查ok_button.png模板")
    else:
        print(f"未知状态: {state}，请检查detect_battle_state函数实现")

def test_start_battle():
    """测试开始战斗功能"""
    print("\n测试开始战斗功能...")
    
    # 创建机器人实例
    bot = ClashRoyaleBot(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 尝试开始战斗
    result = bot.start_battle()
    
    if result:
        print("成功开始战斗!")
        print("是否要执行战斗操作? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            # 执行几次战斗操作
            for i in range(3):
                print(f"执行第{i+1}次战斗操作...")
                bot.perform_battle_actions()
                time.sleep(2)
    else:
        print("无法开始战斗，请检查以下可能的问题:")
        print("1. 模板图像是否正确")
        print("2. 游戏界面是否在正确状态")
        print("3. 置信度是否设置合适")

def run_auto_battle(num_battles=3):
    """运行完整的自动战斗"""
    print(f"\n开始运行自动战斗，计划进行{num_battles}次战斗...")
    
    # 创建机器人实例
    bot = ClashRoyaleBot(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 运行自动战斗循环
    bot.auto_battle_loop(num_battles=num_battles, wait_between=5)

def adjust_template_confidence():
    """调整模板识别置信度并测试"""
    templates_dir = create_template_directory()
    existing_templates, _ = check_existing_templates(templates_dir)
    
    if not existing_templates:
        print("没有可测试的模板")
        return
    
    print("\n请选择要测试的模板:")
    for i, template in enumerate(existing_templates):
        print(f"{i+1}. {template}")
    
    template_choice = input("\n请输入模板编号(0返回): ").strip()
    if template_choice == '0':
        return
    
    try:
        template_index = int(template_choice) - 1
        if 0 <= template_index < len(existing_templates):
            template_name = existing_templates[template_index]
            
            print("\n请输入要测试的置信度(0.1-1.0):")
            confidence = float(input().strip())
            if 0.1 <= confidence <= 1.0:
                test_template(template_name, templates_dir, confidence)
            else:
                print("置信度必须在0.1到1.0之间")
        else:
            print("无效的模板编号")
    except ValueError:
        print("请输入有效的数字")

def diagnose_battle_issues():
    """诊断战斗问题"""
    print("\n开始诊断战斗问题...")
    templates_dir = create_template_directory()
    
    # 检查模板是否存在
    existing_templates, missing_templates = check_existing_templates(templates_dir)
    
    if missing_templates:
        print("\n问题1: 缺少必要的模板图像")
        print("缺失的模板:")
        for template in missing_templates:
            print(f"  - {template}")
        print("建议: 使用'创建缺失的模板'功能创建这些模板")
        return
    
    # 测试关键模板的识别
    print("\n测试关键模板识别...")
    key_templates = ['battle_button.png', 'confirm_battle.png']
    recognition_issues = []
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")