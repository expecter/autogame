import cv2
import numpy as np
import pyautogui
import time
import os
import random
from autogame import AutoGame

class ClashRoyaleBot(AutoGame):
    """
    对战精灵类游戏的自动战斗机器人
    基于图像中显示的游戏界面定制
    """
    def __init__(self, confidence=0.8, region=None):
        super().__init__(confidence, region)
        self.log("对战精灵自动战斗机器人已初始化")
        
        # 游戏特定的状态标志
        self.in_battle = False
        self.elixir_bar = 0  # 法力值/能量条
        self.card_positions = []  # 卡牌位置
        
        # 确保所需的模板存在
        self.check_templates()
    
    def check_templates(self):
        """
        检查必要的模板是否存在，如果不存在则提示用户创建
        """
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
        
        missing_templates = []
        for template in required_templates:
            template_path = os.path.join(self.templates_dir, template)
            if not os.path.exists(template_path):
                missing_templates.append(template)
        
        if missing_templates:
            self.log("警告：以下模板文件不存在，需要创建：")
            for template in missing_templates:
                self.log(f"  - {template}")
            self.log("请使用save_template方法创建这些模板")
    
    def detect_battle_state(self):
        """
        检测当前战斗状态
        :return: 状态描述字符串
        """
        # 检测是否在主界面
        if self.find_template('battle_button.png', confidence=0.7):
            return "main_menu"
        
        # 检测是否在战斗中
        # 这里可以通过识别战斗界面的特定元素来判断
        # 例如能量条、场地等
        
        # 检测是否战斗结束
        if self.find_template('victory_screen.png', confidence=0.7):
            return "victory"
        
        if self.find_template('defeat_screen.png', confidence=0.7):
            return "defeat"
        
        # 默认假设在战斗中
        return "in_battle"
    
    def start_battle(self):
        """
        开始战斗
        :return: 是否成功开始战斗
        """
        state = self.detect_battle_state()
        
        if state == "main_menu":
            # 点击对战按钮
            if not self.click_template('battle_button.png'):
                self.log("无法找到对战按钮")
                return False
            
            # 等待确认对战按钮出现
            time.sleep(1)
            if not self.click_template('confirm_battle.png'):
                self.log("无法找到确认对战按钮")
                return False
            
            # 等待进入战斗
            self.log("等待进入战斗...")
            time.sleep(5)  # 等待加载战斗场景
            
            self.in_battle = True
            return True
        elif state == "in_battle":
            self.log("已经在战斗中")
            self.in_battle = True
            return True
        else:
            self.log(f"当前状态不适合开始战斗: {state}")
            return False
    
    def detect_elixir_bar(self):
        """
        检测当前能量/法力值
        :return: 估计的能量值(0-10)
        """
        # 这里需要根据游戏界面实现能量条检测
        # 可以使用颜色识别或模板匹配等方法
        # 简化版本，随机返回一个值用于测试
        return random.randint(5, 10)
    
    def detect_card_positions(self):
        """
        检测当前可用卡牌的位置
        :return: 卡牌位置列表
        """
        positions = []
        
        # 检测每个卡牌槽位
        for i in range(1, 5):
            card_template = f'card_slot_{i}.png'
            position = self.find_template(card_template, confidence=0.6)
            if position:
                positions.append((position, i))
        
        self.card_positions = positions
        return positions
    
    def play_card(self, card_index, target_position=None):
        """
        打出一张卡牌
        :param card_index: 卡牌索引(1-4)
        :param target_position: 目标位置，如果为None则随机选择
        :return: 是否成功打出卡牌
        """
        # 检测卡牌位置
        self.detect_card_positions()
        
        # 找到对应索引的卡牌
        card_position = None
        for pos, idx in self.card_positions:
            if idx == card_index:
                card_position = pos
                break
        
        if not card_position:
            self.log(f"找不到索引为{card_index}的卡牌")
            return False
        
        # 点击卡牌
        self.click(card_position)
        
        # 如果没有指定目标位置，则在场地中心区域随机选择一个位置
        if target_position is None:
            # 假设游戏场地在屏幕中央区域
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            
            # 在中心区域随机选择一个点
            target_x = center_x + random.randint(-100, 100)
            target_y = center_y + random.randint(-50, 50)
            target_position = (target_x, target_y)
        
        # 点击目标位置放置卡牌
        time.sleep(0.5)  # 短暂延迟，模拟人类操作
        self.click(target_position)
        
        self.log(f"已打出卡牌{card_index}到位置{target_position}")
        return True
    
    def perform_battle_actions(self):
        """
        执行战斗中的操作
        """
        if not self.in_battle:
            self.log("当前不在战斗中，无法执行战斗操作")
            return
        
        # 检测当前能量
        elixir = self.detect_elixir_bar()
        self.log(f"当前能量: {elixir}")
        
        # 简单的战斗策略：能量足够时随机打出卡牌
        if elixir >= 4:  # 假设大多数卡牌需要4点能量
            # 随机选择一张卡牌打出
            card_index = random.randint(1, 4)
            self.play_card(card_index)
            
            # 等待一段时间，让能量恢复
            wait_time = random.uniform(1.5, 3.0)
            self.log(f"等待{wait_time:.1f}秒后继续操作")
            time.sleep(wait_time)
    
    def handle_battle_result(self):
        """
        处理战斗结果
        :return: 战斗结果描述
        """
        # 等待战斗结束画面
        result = None
        wait_start = time.time()
        
        while time.time() - wait_start < 10:  # 最多等待10秒
            state = self.detect_battle_state()
            
            if state == "victory":
                result = "胜利"
                break
            elif state == "defeat":
                result = "失败"
                break
            
            time.sleep(1)
        
        if result:
            self.log(f"战斗结束，结果: {result}")
            
            # 点击确认按钮关闭结果画面
            time.sleep(1)
            self.click_template('ok_button.png')
            
            # 重置战斗状态
            self.in_battle = False
            return result
        else:
            self.log("等待战斗结果超时")
            return "未知"
    
    def create_templates_guide(self):
        """
        创建模板指南，帮助用户创建所需的模板图像
        """
        self.log("=== 创建模板指南 ===")
        self.log("1. 打开游戏并进入主界面")
        self.log("2. 使用以下命令创建对战按钮模板:")
        self.log("   bot.save_template((x, y, width, height), 'battle_button.png')")
        self.log("   其中(x, y, width, height)是对战按钮的屏幕坐标和尺寸")
        self.log("3. 对其他必要元素重复此过程")
        self.log("4. 完成所有模板后，可以开始使用自动战斗功能")

# 示例用法
if __name__ == "__main__":
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
    time.sleep(5)
    
    # 开始自动战斗循环
    print("\n开始自动战斗? (y/n)")
    choice