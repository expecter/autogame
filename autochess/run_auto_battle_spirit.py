import cv2
import numpy as np
import pyautogui
import time
import os
import sys
from auto_battle_spirit import AutoBattleSpirit

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    print("="*50)
    print("对战精灵自动战斗脚本".center(48))
    print("="*50)
    print()

def check_templates():
    """检查必要的模板是否存在"""
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
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
        'gold_coin.png',  # 金币图标
        'refresh_cost.png',  # 刷新卡牌按钮
        'population.png',  # 人口图标
        'buy_card.png',  # 购买卡牌按钮
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
    
    return missing_templates

def main():
    """主函数"""
    clear_screen()
    print_header()
    
    # 检查依赖库
    try:
        import win32gui
        import win32con
    except ImportError:
        print("错误：缺少必要的依赖库 pywin32")
        print("请运行以下命令安装：")
        print("pip install pywin32")
        input("\n按Enter键退出...")
        return
    
    # 检查模板
    missing_templates = check_templates()
    if missing_templates:
        print("警告：以下模板文件不存在，需要先创建：")
        for template in missing_templates:
            print(f"  - {template}")
        print("\n请先运行 python create_templates.py 创建这些模板")
        input("按Enter键退出...")
        return
    
    print("所有必要的模板都已存在，可以开始自动战斗")
    print("\n请选择操作:")
    print("1. 开始自动战斗")
    print("2. 测试窗口句柄获取")
    print("3. 测试模板识别")
    print("0. 退出")
    
    choice = input("\n请输入选项编号: ").strip()
    
    if choice == '1':
        # 设置游戏窗口标题
        window_title = input("请输入游戏窗口标题(默认为'对战精灵'): ").strip() or "对战精灵"
        
        # 创建机器人实例
        bot = AutoBattleSpirit(window_title=window_title, confidence=0.7)
        
        # 设置战斗次数
        num_battles = 3
        try:
            num_battles = int(input("请输入要进行的战斗次数(默认3): ") or "3")
        except ValueError:
            print("输入无效，使用默认值3")
        
        # 尝试查找游戏窗口
        if not bot.hwnd:
            print("未找到游戏窗口，请确保游戏已启动且窗口标题正确")
            input("\n按Enter键返回主菜单...")
            main()
            return
        
        print(f"找到游戏窗口，句柄: {bot.hwnd}")
        print(f"窗口位置: {bot.window_rect}")
        print(f"客户区位置: {bot.client_rect}")
        
        # 给用户5秒时间准备
        print("将在5秒后开始自动战斗...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # 开始自动战斗循环
        result = bot.auto_battle_loop(num_battles=num_battles)
        
        print("\n自动战斗已完成")
        print(f"总战斗次数: {result['battles']}")
        print(f"胜利次数: {result['victories']}")
        print(f"失败次数: {result['defeats']}")
        
        input("\n按Enter键返回主菜单...")
        main()
    
    elif choice == '2':
        # 测试窗口句柄获取
        window_title = input("请输入游戏窗口标题(默认为'对战精灵'): ").strip() or "对战精灵"
        bot = AutoBattleSpirit(window_title=window_title, confidence=0.7)
        
        if bot.hwnd:
            print(f"成功找到游戏窗口，句柄: {bot.hwnd}")
            print(f"窗口位置: {bot.window_rect}")
            print(f"客户区位置: {bot.client_rect}")
            
            print("\n是否激活该窗口? (y/n)")
            if input().strip().lower() == 'y':
                bot.activate_window()
                print("已激活游戏窗口")
        else:
            print(f"未找到标题包含 '{window_title}' 的窗口")
        
        input("\n按Enter键返回主菜单...")
        main()
    
    elif choice == '3':
        # 测试模板识别
        window_title = input("请输入游戏窗口标题(默认为'对战精灵'): ").strip() or "对战精灵"
        bot = AutoBattleSpirit(window_title=window_title, confidence=0.7)
        
        if not bot.hwnd:
            print("未找到游戏窗口，无法进行模板识别测试")
            input("\n按Enter键返回主菜单...")
            main()
            return
        
        print("\n请选择要测试的模板:")
        print("1. 对战按钮")
        print("2. 确认对战按钮")
        print("3. 胜利画面")
        print("4. 失败画面")
        print("5. 确认按钮")
        print("6. 卡牌槽位")
        print("0. 返回")
        
        test_choice = input("\n请输入选项编号: ").strip()
        
        template_map = {
            '1': 'battle_button.png',
            '2': 'confirm_battle.png',
            '3': 'victory_screen.png',
            '4': 'defeat_screen.png',
            '5': 'ok_button.png',
            '6': 'card_slot_1.png'
        }
        
        if test_choice in template_map:
            template_name = template_map[test_choice]
            print(f"\n正在识别模板: {template_name}")
            
            # 激活窗口并截图
            bot.activate_window()
            time.sleep(1)  # 等待窗口激活
            
            # 查找模板
            position = bot.find_template(template_name, confidence=0.7)
            if position:
                print(f"成功识别模板，位置: {position}")
                print("是否点击该位置? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击识别到的位置")
            else:
                print(f"未能识别模板 {template_name}，请检查模板是否正确或调整置信度")
        
        input("\n按Enter键返回主菜单...")
        main()
    
    elif choice == '0':
        print("感谢使用对战精灵自动战斗脚本，再见！")
        return
    else:
        print("无效的选项，请重新选择")
        time.sleep(1)
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        input("按Enter键退出...")