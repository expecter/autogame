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
    print("模板创建向导".center(48))
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
        cv2.waitKey(1000)  # 显示1秒
        cv2.destroyAllWindows()
    
    return True

def test_template(template_name, templates_dir):
    """测试模板识别"""
    print(f"\n测试模板: {template_name}")
    
    # 创建AutoGame实例用于测试
    auto_game = AutoGame(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 尝试识别模板
    position = auto_game.find_template(template_name, confidence=0.7)
    
    if position:
        print(f"成功识别模板 {template_name} 在位置 {position}")
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

def main():
    """主函数"""
    clear_screen()
    print_header()
    
    # 创建模板目录
    templates_dir = create_template_directory()
    
    # 检查现有模板
    existing_templates, missing_templates = check_existing_templates(templates_dir)
    
    print(f"\n已存在的模板 ({len(existing_templates)}/{len(list_required_templates())}):\n")
    for i, template in enumerate(existing_templates):
        print(f"{i+1}. {template}")
    
    print(f"\n缺失的模板 ({len(missing_templates)}/{len(list_required_templates())}):\n")
    for i, template in enumerate(missing_templates):
        print(f"{i+1}. {template}")
    
    # 菜单选项
    while True:
        print("\n请选择操作:")
        print("1. 创建缺失的模板")
        print("2. 重新创建特定模板")
        print("3. 测试模板识别")
        print("4. 调整识别置信度")
        print("0. 退出")
        
        choice = input("\n请输入选项编号: ").strip()
        
        if choice == '1':
            if not missing_templates:
                print("没有缺失的模板需要创建")
                continue
            
            print("\n开始创建缺失的模板...")
            for template in missing_templates:
                capture_template(template, templates_dir)
            
            # 更新模板列表
            existing_templates, missing_templates = check_existing_templates(templates_dir)
        
        elif choice == '2':
            print("\n请选择要重新创建的模板:")
            all_templates = list_required_templates()
            for i, template in enumerate(all_templates):
                status = "[已存在]" if template in existing_templates else "[缺失]"
                print(f"{i+1}. {template} {status}")
            
            template_choice = input("\n请输入模板编号(0返回): ").strip()
            if template_choice == '0':
                continue
            
            try:
                template_index = int(template_choice) - 1
                if 0 <= template_index < len(all_templates):
                    capture_template(all_templates[template_index], templates_dir)
                    # 更新模板列表
                    existing_templates, missing_templates = check_existing_templates(templates_dir)
                else:
                    print("无效的模板编号")
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '3':
            if not existing_templates:
                print("没有可测试的模板")
                continue
            
            print("\n请选择要测试的模板:")
            for i, template in enumerate(existing_templates):
                print(f"{i+1}. {template}")
            
            template_choice = input("\n请输入模板编号(0返回): ").strip()
            if template_choice == '0':
                continue
            
            try:
                template_index = int(template_choice) - 1
                if 0 <= template_index < len(existing_templates):
                    test_template(existing_templates[template_index], templates_dir)
                else:
                    print("无效的模板编号")
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '4':
            print("\n调整识别置信度可以提高或降低模板匹配的严格程度")
            print("较高的置信度(如0.9)要求更精确的匹配，但可能导致无法识别")
            print("较低的置信度(如0.6)更宽松，但可能导致错误识别")
            
            current_confidence = 0.7  # 默认值
            print(f"当前默认置信度: {current_confidence}")
            
            new_confidence = input("请输入新的置信度(0.1-1.0，或按Enter保持不变): ").strip()
            if new_confidence:
                try:
                    new_confidence = float(new_confidence)
                    if 0.1 <= new_confidence <= 1.0:
                        print(f"置信度已调整为: {new_confidence}")
                        # 这里可以添加保存置信度设置的代码
                    else:
                        print("置信度必须在0.1到1.0之间")
                except ValueError:
                    print("请输入有效的数字")
        
        elif choice == '0':
            break
        
        else:
            print("无效的选项，请重新输入")

if __name__ == "__main__":
    main()