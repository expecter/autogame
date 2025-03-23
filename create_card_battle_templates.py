import cv2
import numpy as np
import pyautogui
import time
import os
import sys
from autogame import AutoGame

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    print("="*50)
    print("卡牌对战游戏模板创建向导".center(48))
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
        'energy_full.png',  # 能量满格指示
        'enemy_tower.png',  # 敌方塔
        'ally_tower.png',  # 我方塔
        'upgrade_population.png',  # 升级人口按钮
        'refresh_cards.png',  # 刷新卡牌按钮
        'same_card.png',  # 同名卡牌识别
        'buy_card.png',  # 可购买的卡牌
        'gold_coin.png',  # 金币图标
        'refresh_cost.png',  # 刷新卡牌消耗
        'population.png',  # 人口数量/上限
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
        
        # 显示图像
        cv2.imshow(template_name, display_img)
        cv2.waitKey(1000)  # 显示1秒
        cv2.destroyAllWindows()
    
    return True

def create_templates():
    """创建模板的主函数"""
    clear_screen()
    print_header()
    
    # 创建模板目录
    templates_dir = create_template_directory()
    
    # 检查已存在的模板
    existing_templates, missing_templates = check_existing_templates(templates_dir)
    
    if existing_templates:
        print("\n已存在的模板:")
        for template in existing_templates:
            print(f"  - {template}")
    
    if not missing_templates:
        print("\n所有必要的模板都已存在！")
        input("按Enter键继续...")
        return
    
    print("\n需要创建的模板:")
    for template in missing_templates:
        print(f"  - {template}")
    
    print("\n准备创建模板...")
    print("请确保游戏窗口可见，并且不被其他窗口遮挡")
    input("准备好后按Enter键开始...")
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 创建缺失的模板
    for template in missing_templates:
        success = capture_template(template, templates_dir)
        if not success:
            print(f"创建模板 {template} 失败，请重试")
            input("按Enter键继续...")
        else:
            print(f"成功创建模板 {template}")
            time.sleep(1)
    
    print("\n所有模板创建完成！")
    input("按Enter键继续...")

def main():
    create_templates()

if __name__ == "__main__":
    main()