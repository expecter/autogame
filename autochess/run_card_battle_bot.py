import cv2
import numpy as np
import pyautogui
import time
import os
import sys
from advanced_battle_bot import AdvancedBattleBot

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    print("="*50)
    print("卡牌对战游戏自动战斗脚本".center(48))
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
        'enemy_tower.png',  # 敌方塔
        'ally_tower.png',  # 我方塔
        'upgrade_population.png',  # 升级人口按钮
        'refresh_cards.png',  # 刷新卡牌按钮
        'same_card.png',  # 同名卡牌识别
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
    
    # 检查模板
    missing_templates = check_templates()
    if missing_templates:
        print("警告：以下模板文件不存在，需要先创建：")
        for template in missing_templates:
            print(f"  - {template}")
        print("\n请先运行 python create_card_battle_templates.py 创建这些模板")
        input("按Enter键退出...")
        return
    
    print("所有必要的模板都已存在，可以开始自动战斗")
    print("\n请选择操作:")
    print("1. 开始自动战斗")
    print("2. 测试模板识别")
    print("0. 退出")
    
    choice = input("\n请输入选项编号: ").strip()
    
    if choice == '1':
        # 创建机器人实例
        bot = AdvancedBattleBot(confidence=0.7)
        
        # 设置战斗次数
        num_battles = 3
        try:
            num_battles = int(input("请输入要进行的战斗次数(默认3): ") or "3")
        except ValueError:
            print("输入无效，使用默认值3")
        
        # 给用户5秒时间切换到游戏窗口
        print("请在5秒内切换到游戏窗口...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        if test_choice == '1':
            # 测试战斗状态检测
            state = bot.detect_battle_state()
            print(f"\n检测到的战斗状态: {state}")
            input("\n按Enter键继续...")
        
        elif test_choice == '2':
            # 测试升级人口按钮识别
            position = bot.find_template('upgrade_population.png', confidence=0.7)
            if position:
                print(f"\n成功识别升级人口按钮，位置: {position}")
                print("是否点击该按钮? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击升级人口按钮")
            else:
                print("\n无法识别升级人口按钮，请检查模板或调整置信度")
            input("\n按Enter键继续...")
        
        elif test_choice == '3':
            # 测试刷新卡牌按钮识别
            position = bot.find_template('refresh_cards.png', confidence=0.7)
            if position:
                print(f"\n成功识别刷新卡牌按钮，位置: {position}")
                print("是否点击该按钮? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击刷新卡牌按钮")
            else:
                print("\n无法识别刷新卡牌按钮，请检查模板或调整置信度")
            input("\n按Enter键继续...")
        
        elif test_choice == '4':
            # 测试同名卡牌识别
            position = bot.find_template('same_card.png', confidence=0.7)
            if position:
                print(f"\n成功识别同名卡牌，位置: {position}")
                print("是否点击该卡牌进行合并? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击同名卡牌进行合并")
            else:
                print("\n无法识别同名卡牌，请检查模板或调整置信度")
            input("\n按Enter键继续...")
        
        # 返回主菜单
        main()
        
        # 开始自动战斗循环
        bot.auto_battle_loop(num_battles=num_battles)
    
    elif choice == '2':
        # 创建机器人实例用于测试
        bot = AdvancedBattleBot(confidence=0.7)
        
        print("\n请选择要测试的功能:")
        print("1. 测试战斗状态检测")
        print("2. 测试升级人口按钮识别")
        print("3. 测试刷新卡牌按钮识别")
        print("4. 测试同名卡牌识别")
        print("0. 返回")
        
        test_choice = input("\n请输入选项编号: ").strip()
        
        # 给用户5秒时间切换到游戏窗口
        print("请在5秒内切换到游戏窗口...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        if test_choice == '1':
            # 测试战斗状态检测
            state = bot.detect_battle_state()
            print(f"\n检测到的战斗状态: {state}")
            input("\n按Enter键继续...")
        
        elif test_choice == '2':
            # 测试升级人口按钮识别
            position = bot.find_template('upgrade_population.png', confidence=0.7)
            if position:
                print(f"\n成功识别升级人口按钮，位置: {position}")
                print("是否点击该按钮? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击升级人口按钮")
            else:
                print("\n无法识别升级人口按钮，请检查模板或调整置信度")
            input("\n按Enter键继续...")
        
        elif test_choice == '3':
            # 测试刷新卡牌按钮识别
            position = bot.find_template('refresh_cards.png', confidence=0.7)
            if position:
                print(f"\n成功识别刷新卡牌按钮，位置: {position}")
                print("是否点击该按钮? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击刷新卡牌按钮")
            else:
                print("\n无法识别刷新卡牌按钮，请检查模板或调整置信度")
            input("\n按Enter键继续...")
        
        elif test_choice == '4':
            # 测试同名卡牌识别
            position = bot.find_template('same_card.png', confidence=0.7)
            if position:
                print(f"\n成功识别同名卡牌，位置: {position}")
                print("是否点击该卡牌进行合并? (y/n)")
                if input().strip().lower() == 'y':
                    bot.click(position)
                    print("已点击同名卡牌进行合并")
            else:
                print("\n无法识别同名卡牌，请检查模板或调整置信度")
            input("\n按Enter键继续...")
        
        # 返回主菜单
        main()