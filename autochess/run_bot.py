import os
import sys
import time

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    print("="*50)
    print("自动游戏战斗机器人启动器".center(48))
    print("="*50)
    print()

def check_dependencies():
    """检查依赖项是否已安装"""
    try:
        import cv2
        import numpy
        import pyautogui
        from PIL import Image
        return True
    except ImportError as e:
        print(f"错误: 缺少必要的依赖项 - {str(e)}")
        print("请运行以下命令安装依赖项:")
        print("pip install -r requirements.txt")
        return False

def main_menu():
    """显示主菜单"""
    clear_screen()
    print_header()
    print("请选择要运行的机器人类型:")
    print("1. 基础战斗机器人 (ClashRoyaleBot)")
    print("2. 高级战斗机器人 (AdvancedBattleBot)")
    print("3. 运行模板创建向导")
    print("4. 查看帮助文档")
    print("0. 退出程序")
    print()
    
    choice = input("请输入选项编号: ").strip()
    return choice

def run_basic_bot():
    """运行基础战斗机器人"""
    clear_screen()
    print_header()
    print("正在启动基础战斗机器人...")
    
    try:
        from clash_royale_bot import ClashRoyaleBot
        # 创建机器人实例
        bot = ClashRoyaleBot(confidence=0.7)
        
        # 检查是否有缺失的模板
        print("\n是否要创建模板指南？(y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            bot.create_templates_guide()
            
            # 提供一个简单的方式来创建模板
            print("\n是否要进入模板创建模式？(y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                print("请将鼠标移动到要截图的区域左上角，然后按Enter")
                input()
                import pyautogui
                start_x, start_y = pyautogui.position()
                
                print("现在将鼠标移动到区域右下角，然后按Enter")
                input()
                end_x, end_y = pyautogui.position()
                
                width = end_x - start_x
                height = end_y - start_y
                
                print(f"选择的区域: ({start_x}, {start_y}, {width}, {height})")
                print("请输入模板名称(例如: battle_button.png):")
                template_name = input().strip()
                
                bot.save_template((start_x, start_y, width, height), template_name)
                print(f"已保存模板: {template_name}")
        
        # 给用户5秒时间切换到游戏窗口
        print("\n请在5秒内切换到游戏窗口...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # 开始自动战斗循环
        print("\n开始自动战斗? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            num_battles = 3
            try:
                num_battles = int(input("请输入要进行的战斗次数: "))
            except ValueError:
                print("输入无效，使用默认值3")
            
            bot.auto_battle_loop(num_battles=num_battles, wait_between=3)
        
    except Exception as e:
        print(f"错误: {str(e)}")
    
    input("\n按Enter键返回主菜单...")

def run_advanced_bot():
    """运行高级战斗机器人"""
    clear_screen()
    print_header()
    print("正在启动高级战斗机器人...")
    
    try:
        from advanced_battle_bot import AdvancedBattleBot
        # 创建机器人实例
        bot = AdvancedBattleBot(confidence=0.7)
        
        # 检查是否有缺失的模板
        print("\n是否要运行模板创建向导？(y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            # 导入并运行模板创建向导
            import template_creator
            template_creator.main()
        
        # 给用户5秒时间切换到游戏窗口
        print("\n请在5秒内切换到游戏窗口...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # 开始自动战斗循环
        print("\n开始自动战斗? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            num_battles = 3
            try:
                num_battles = int(input("请输入要进行的战斗次数: "))
            except ValueError:
                print("输入无效，使用默认值3")
            
            # 设置战斗区域
            bot.setup_battle_areas()
            
            # 开始战斗循环
            battles_completed = 0
            
            try:
                while battles_completed < num_battles:
                    print(f"\n开始第 {battles_completed + 1} 次战斗")
                    
                    # 开始战斗
                    if not bot.start_battle():
                        print("无法开始战斗，等待后重试")
                        time.sleep(3)
                        continue
                    
                    # 战斗中的操作循环
                    battle_duration = 0
                    max_battle_time = 180  # 最长战斗时间3分钟
                    
                    while battle_duration < max_battle_time:
                        # 检查战斗是否结束
                        state = bot.detect_battle_state()
                        if state in ["victory", "defeat"]:
                            break
                        
                        # 执行战斗操作
                        bot.perform_battle_actions()
                        
                        # 增加战斗时间
                        battle_duration += 3  # 假设每次操作约3秒
                    
                    # 处理战斗结果
                    result = bot.handle_battle_result()
                    print(f"战斗结果: {result}")
                    
                    battles_completed += 1
                    
                    # 战斗间隔
                    if battles_completed < num_battles:
                        wait_time = 5
                        print(f"等待 {wait_time} 秒后开始下一次战斗")
                        time.sleep(wait_time)
                
                print(f"\n自动战斗完成，共进行了 {battles_completed} 次战斗")
                
            except KeyboardInterrupt:
                print("\n用户中断了自动战斗")
            except Exception as e:
                print(f"\n自动战斗出错: {str(e)}")
    
    except Exception as e:
        print(f"错误: {str(e)}")
    
    input("\n按Enter键返回主菜单...")

def run_template_creator():
    """运行模板创建向导"""
    clear_screen()
    print_header()
    print("正在启动模板创建向导...")
    
    try:
        import template_creator
        template_creator.main()
    except Exception as e:
        print(f"错误: {str(e)}")
    
    input("\n按Enter键返回主菜单...")

def show_help():
    """显示帮助文档"""
    clear_screen()
    print_header()
    print("=== 自动游戏战斗机器人使用帮助 ===")
    print()
    print("1. 基础战斗机器人")
    print("   - 适用于简单的对战游戏")
    print("   - 提供基本的战斗自动化功能")
    print()
    print("2. 高级战斗机器人")
    print("   - 适用于复杂的对战游戏")
    print("   - 提供更智能的战斗策略和决策")
    print("   - 支持更多的游戏元素识别")
    print()
    print("3. 模板创建向导")
    print("   - 帮助创建游戏界面元素的模板图像")
    print("   - 用于训练机器人识别游戏元素")
    print()
    print("注意事项:")
    print("- 使用前请确保游戏窗口可见且不被遮挡")
    print("- 运行过程中将鼠标移动到屏幕左上角可紧急停止")
    print("- 如果游戏界面发生变化，需要重新创建模板")
    print()
    
    input("按Enter键返回主菜单...")

def main():
    """主函数"""
    # 检查依赖项
    if not check_dependencies():
        input("\n按Enter键退出程序...")
        return
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            run_basic_bot()
        elif choice == '2':
            run_advanced_bot()
        elif choice == '3':
            run_template_creator()
        elif choice == '4':
            show_help()
        elif choice == '0':
            clear_screen()
            print("感谢使用自动游戏战斗机器人！")
            break
        else:
            print("无效的选项，请重新选择")
            time.sleep(1)

if __name__ == "__main__":
    main()