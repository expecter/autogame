import cv2
import numpy as np
import pyautogui
import time
import random
import os
import win32gui
import win32con
import win32ui
import win32api
from ctypes import windll
from PIL import Image
from autogame import AutoGame

class AutoBattleSpirit(AutoGame):
    """
    对战精灵游戏的自动战斗机器人
    能够自动获取游戏窗口句柄，并在指定窗口内进行操作
    """
    def __init__(self, window_title="对战精灵", confidence=0.8):
        """
        初始化自动对战精灵机器人
        :param window_title: 游戏窗口标题，用于查找窗口句柄
        :param confidence: 图像匹配的置信度阈值
        """
        super().__init__(confidence=confidence)
        self.log("对战精灵自动战斗机器人已初始化")
        
        # 窗口相关属性
        self.window_title = window_title
        self.hwnd = None  # 窗口句柄
        self.window_rect = None  # 窗口矩形区域
        self.client_rect = None  # 客户区矩形区域
        
        # 游戏特定的状态标志
        self.in_battle = False
        self.energy = 0  # 能量值
        self.gold = 0  # 金币数量
        self.card_positions = []  # 卡牌位置
        self.population = 0  # 当前人口
        self.max_population = 0  # 最大人口
        self.relic_selected = False  # 是否已选择圣物
        
        # 初始化窗口句柄
        self.find_game_window()
        
        # 确保所需的模板存在
        self.check_templates()
    
    def find_game_window(self):
        """
        查找游戏窗口并获取窗口句柄
        :return: 是否成功获取窗口句柄
        """
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if self.window_title in window_text:
                    hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        
        if hwnds:
            self.hwnd = hwnds[0]  # 使用找到的第一个匹配窗口
            self.log(f"找到游戏窗口，句柄: {self.hwnd}")
            
            # 获取窗口位置和大小
            self.update_window_rect()
            return True
        else:
            self.log(f"未找到标题包含 '{self.window_title}' 的窗口")
            return False
    
    def update_window_rect(self):
        """
        更新窗口位置和大小信息
        """
        if self.hwnd:
            # 获取窗口矩形（包括边框和标题栏）
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            self.window_rect = (left, top, right - left, bottom - top)
            
            # 获取客户区矩形（不包括边框和标题栏）
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            client_left, client_top = win32gui.ClientToScreen(self.hwnd, (left, top))
            client_right, client_bottom = win32gui.ClientToScreen(self.hwnd, (right, bottom))
            self.client_rect = (client_left, client_top, client_right - client_left, client_bottom - client_top)
            
            self.log(f"窗口位置: {self.window_rect}")
            self.log(f"客户区位置: {self.client_rect}")
            
            # 更新截图区域为客户区
            self.region = self.client_rect
    
    def activate_window(self):
        """
        激活游戏窗口，使其成为前台窗口
        :return: 是否成功激活窗口
        """
        if not self.hwnd:
            if not self.find_game_window():
                return False
        
        # 如果窗口最小化，则恢复
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        
        # 将窗口设为前台
        win32gui.SetForegroundWindow(self.hwnd)
        time.sleep(0.5)  # 等待窗口激活
        
        # 更新窗口位置信息
        self.update_window_rect()
        return True
    
    def take_screenshot(self):
        """
        获取游戏窗口的截图
        :return: 游戏窗口截图的numpy数组
        """
        if not self.hwnd:
            if not self.find_game_window():
                return None
        
        # 确保窗口处于激活状态
        self.activate_window()
        
        # 使用父类的截图方法，但限定在客户区范围内
        return super().take_screenshot()
    
    def click(self, position, random_offset=5):
        """
        在游戏窗口内点击指定位置
        :param position: (x, y) 坐标元组，相对于屏幕的绝对坐标
        :param random_offset: 随机偏移的最大像素数
        :return: 是否成功点击
        """
        if position is None:
            self.log("无法点击：位置为None")
            return False
        
        # 确保窗口处于激活状态
        if not self.activate_window():
            self.log("无法激活窗口，点击操作取消")
            return False
        
        # 执行点击操作
        return super().click(position, random_offset)
    
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
            'energy_full.png',  # 能量满格指示
            'gold_coin.png',  # 金币图标
            'refresh_cost.png',  # 刷新卡牌按钮
            'population.png',  # 人口图标
            'buy_card.png',  # 购买卡牌按钮
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
            self.log("请使用模板创建向导创建这些模板")
    
    def detect_battle_state(self):
        """
        检测当前战斗状态
        :return: 状态描述字符串
        """
        # 检测是否在主界面
        if self.find_template('battle_button.png', confidence=0.7):
            return "main_menu"
        
        # 检测是否在圣物选择界面
        # 通过检测特定文字或界面元素来判断
        # 这里假设有一个圣物选择的特征可以识别
        if not self.relic_selected and self.detect_relic_selection_screen():
            return "relic_selection"
        
        # 检测是否战斗结束
        if self.find_template('victory_screen.png', confidence=0.7):
            return "victory"
        
        if self.find_template('defeat_screen.png', confidence=0.7):
            return "defeat"
        
        # 默认假设在战斗中
        return "in_battle"
    
    def detect_relic_selection_screen(self):
        """
        检测是否在圣物选择界面
        :return: 是否在圣物选择界面
        """
        # 实际实现中，可以通过识别界面特征来判断
        # 例如检测"选择一个圣物"的文字或特定的界面布局
        # 这里简化实现，通过截图分析来判断
        
        # 获取屏幕截图
        screen = self.take_screenshot()
        if screen is None:
            return False
        
        # 转换为灰度图像
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        
        # 在图像中间区域查找亮度较高的区域，这通常是圣物选择界面的特征
        # 这是一个简化的实现，实际应用中可能需要更复杂的图像处理
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        
        # 如果中心区域的平均亮度高于阈值，可能是圣物选择界面
        avg_brightness = np.mean(center_region)
        if avg_brightness > 100:  # 阈值可以根据实际情况调整
            return True
        
        return False
    
    def select_relic(self):
        """
        在圣物选择界面选择一个圣物
        :return: 是否成功选择圣物
        """
        self.log("检测到圣物选择界面，准备选择圣物")
        
        # 获取屏幕截图
        screen = self.take_screenshot()
        if screen is None:
            self.log("无法获取屏幕截图，圣物选择失败")
            return False
        
        # 假设圣物选择界面有三个选项，分别位于屏幕的左中右位置
        h, w, _ = screen.shape
        
        # 计算三个圣物的大致位置
        left_relic = (w // 4, h // 2)
        middle_relic = (w // 2, h // 2)
        right_relic = (3 * w // 4, h // 2)
        
        # 随机选择一个圣物
        relics = [left_relic, middle_relic, right_relic]
        selected_relic = random.choice(relics)
        
        # 点击选择的圣物
        self.log(f"随机选择圣物，位置: {selected_relic}")
        if self.click(selected_relic):
            self.log("成功选择圣物")
            self.relic_selected = True
            time.sleep(2)  # 等待选择动画完成
            return True
        else:
            self.log("圣物选择失败")
            return False
    
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
            
            # 等待进入战斗或圣物选择界面
            self.log("等待进入战斗或圣物选择界面...")
            time.sleep(5)  # 等待加载场景
            
            # 检查是否进入了圣物选择界面
            if self.detect_relic_selection_screen():
                self.log("检测到圣物选择界面")
                if not self.select_relic():
                    self.log("圣物选择失败")
                    return False
                # 等待进入战斗
                time.sleep(3)
            
            self.in_battle = True
            # 重置圣物选择状态，为下一场战斗做准备
            self.relic_selected = False
            return True
        elif state == "relic_selection":
            # 如果直接在圣物选择界面
            self.log("当前在圣物选择界面")
            if not self.select_relic():
                self.log("圣物选择失败")
                return False
            # 等待进入战斗
            time.sleep(3)
            self.in_battle = True
            return True
        elif state == "in_battle":
            self.log("已经在战斗中")
            self.in_battle = True
            return True
        else:
            self.log(f"当前状态不适合开始战斗: {state}")
            return False
    
    def detect_energy(self):
        """
        检测当前能量值
        :return: 估计的能量值
        """
        # 实际实现中，可以通过识别能量条的颜色或长度来判断
        # 这里使用简化版本，通过查找能量满格指示器来判断
        if self.find_template('energy_full.png', confidence=0.7):
            return 10
        
        # 简化版本，随机返回一个值用于测试
        return random.randint(5, 9)
    
    def detect_gold(self):
        """
        检测当前金币数量
        :return: 估计的金币数量
        """
        # 查找金币图标位置
        gold_icon_pos = self.find_template('gold_coin.png', confidence=0.7)
        if not gold_icon_pos:
            self.log("无法找到金币图标")
            return 0
        
        # 实际实现中，应该通过OCR识别金币图标旁边的数字
        # 这里使用简化版本，假设金币数量显示在金币图标右侧
        # 获取屏幕截图
        screen = self.take_screenshot()
        if screen is None:
            return 0
        
        # 在金币图标右侧区域查找数字
        # 这里简化实现，返回一个随机值用于测试
        # 实际应用中应该使用OCR技术识别数字
        self.gold = random.randint(10, 50)  # 假设金币范围在10-50之间
        self.log(f"当前金币: {self.gold}")
        return self.gold
    
    def detect_population(self):
        """
        检测当前人口和最大人口
        :return: (当前人口, 最大人口)元组
        """
        # 查找人口图标位置
        population_icon_pos = self.find_template('population.png', confidence=0.7)
        if not population_icon_pos:
            self.log("无法找到人口图标")
            return (0, 0)
        
        # 实际实现中，应该通过OCR识别人口图标旁边的数字
        # 这里使用简化版本，假设人口显示在人口图标下方
        # 获取屏幕截图
        screen = self.take_screenshot()
        if screen is None:
            return (0, 0)
        
        # 在人口图标下方区域查找数字
        # 这里简化实现，返回随机值用于测试
        # 实际应用中应该使用OCR技术识别数字
        self.population = random.randint(0, 5)  # 假设当前人口范围在0-5之间
        self.max_population = random.randint(5, 10)  # 假设最大人口范围在5-10之间
        
        # 确保当前人口不超过最大人口
        if self.population > self.max_population:
            self.population = self.max_population
        
        self.log(f"当前人口: {self.population}/{self.max_population}")
        return (self.population, self.max_population)
    
    def upgrade_population(self):
        """
        升级人口上限
        :return: 是否成功升级
        """
        # 检测当前人口和金币
        self.detect_population()
        self.detect_gold()
        
        # 假设升级人口的按钮在屏幕左下角
        # 实际实现中，应该通过模板匹配找到升级按钮
        # 这里简化实现，假设升级按钮的位置是固定的
        if self.client_rect:
            upgrade_button_x = self.client_rect[0] + self.client_rect[2] // 4
            upgrade_button_y = self.client_rect[1] + self.client_rect[3] * 3 // 4
            upgrade_button_pos = (upgrade_button_x, upgrade_button_y)
            
            # 点击升级按钮
            self.log("尝试升级人口上限")
            if self.click(upgrade_button_pos):
                self.log("已点击升级按钮")
                # 假设升级成功，增加最大人口
                self.max_population += 1
                self.log(f"升级成功，当前人口上限: {self.max_population}")
                return True
        
        self.log("升级人口失败")
        return False
    
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
    
    def detect_shop_cards(self):
        """
        检测商店中可购买的卡牌位置
        :return: 卡牌位置列表
        """
        # 获取屏幕截图
        screen = self.take_screenshot()
        if screen is None:
            return []
        
        # 假设商店卡牌在屏幕底部，水平排列
        h, w, _ = screen.shape
        
        # 计算三个卡牌的大致位置
        left_card = (w // 4, h * 3 // 4)
        middle_card = (w // 2, h * 3 // 4)
        right_card = (3 * w // 4, h * 3 // 4)
        
        # 返回卡牌位置列表
        return [left_card, middle_card, right_card]
        
    def select_card_to_buy(self):
        """
        从商店中选择一张卡牌购买
        可以随机选择或根据特定策略选择
        :return: 选择的卡牌位置坐标
        """
        # 获取可购买的卡牌位置
        shop_cards = self.detect_shop_cards()
        
        if not shop_cards:
            self.log("商店中没有可购买的卡牌")
            return None
        
        # 随机选择一张卡牌
        selected_card = random.choice(shop_cards)
        self.log(f"选择了一张卡牌，位置: {selected_card}")
        
        return selected_card
    
    def auto_buy_card(self):
        """
        自动从商店中选择并购买一张卡牌
        :return: 是否成功购买
        """
        # 选择一张卡牌
        card_position = self.select_card_to_buy()
        
        if card_position is None:
            return False
        
        # 购买选择的卡牌
        return self.buy_card(card_position)
    
    def buy_card(self, card_position=None):
        """
        购买指定位置的卡牌，如果不指定位置则随机选择一张
        :param card_position: 卡牌位置坐标，如果为None则随机选择
        :return: 是否成功购买
        """
        # 获取可购买的卡牌位置
        shop_cards = self.detect_shop_cards()
        
        if not shop_cards:
            self.log("商店中没有可购买的卡牌")
            return False
        
        # 如果没有指定卡牌位置，则随机选择一张
        if card_position is None:
            card_position = random.choice(shop_cards)
            self.log(f"随机选择了一张卡牌，位置: {card_position}")
        
        # 点击卡牌进行购买
        self.log(f"尝试购买卡牌，位置: {card_position}")
        if self.click(card_position):
            # 等待购买动画完成
            time.sleep(0.5)
            self.log(f"购买卡牌成功")
            return True
        else:
            self.log("购买卡牌失败")
            return False
    
    def refresh_shop(self):
        """
        刷新商店卡牌
        :return: 是否成功刷新
        """
        # 查找刷新按钮
        refresh_button_pos = self.find_template('refresh_cost.png', confidence=0.7)
        if not refresh_button_pos:
            self.log("无法找到刷新按钮")
            return False
        
        # 点击刷新按钮
        self.log("尝试刷新卡牌")
        if self.click(refresh_button_pos):
            # 等待刷新动画完成
            time.sleep(0.5)
            
            self.log("刷新卡牌成功")
            return True
        else:
            self.log("刷新卡牌失败")
            return False
    
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
            # 获取客户区中心位置
            if self.client_rect:
                center_x = self.client_rect[0] + self.client_rect[2] // 2
                center_y = self.client_rect[1] + self.client_rect[3] // 2
                
                # 在中心区域随机选择一个点
                target_x = center_x + random.randint(-100, 100)
                target_y = center_y + random.randint(-50, 50)
                target_position = (target_x, target_y)
            else:
                # 如果没有客户区信息，使用屏幕中心
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
        
        # 检测当前能量、金币和人口
        energy = self.detect_energy()
        gold = self.detect_gold()
        population, max_population = self.detect_population()
        
        self.log(f"当前状态 - 能量: {energy}, 金币: {gold}, 人口: {population}/{max_population}")
        
        # 战斗策略：
        # 1. 如果人口未满且有足够金币，优先升级人口
        # 2. 检查商店卡牌，购买最佳卡牌
        # 3. 如果有足够金币且商店卡牌不理想，刷新商店
        # 4. 能量足够时打出手牌
        # 5. 金币用完时结束回合
        
        # 1. 升级人口
        if population < max_population and gold >= 5:  # 假设升级人口需要5金币
            self.upgrade_population()
            # 更新金币
            gold = self.detect_gold()
        
        # 2. 购买卡牌
        shop_cards = self.detect_shop_cards()
        if shop_cards and gold >= 3:  # 假设卡牌价格为3金币
            # 简单策略：随机选择一张卡牌购买
            card_to_buy = random.choice(shop_cards)
            if self.buy_card(card_to_buy):
                # 更新金币
                gold = self.detect_gold()
        
        # 3. 刷新商店
        if gold >= 2:  # 假设刷新价格为2金币
            # 随机决定是否刷新，概率为50%
            if random.random() > 0.5:
                if self.refresh_shop():
                    # 更新金币
                    gold = self.detect_gold()
                    
                    # 刷新后再次尝试购买卡牌
                    shop_cards = self.detect_shop_cards()
                    if shop_cards and gold >= 3:
                        card_to_buy = random.choice(shop_cards)
                        if self.buy_card(card_to_buy):
                            # 更新金币
                            gold = self.detect_gold()
        
        # 4. 打出手牌
        if energy >= 4:  # 假设大多数卡牌需要4点能量
            # 随机选择一张卡牌打出
            card_index = random.randint(1, 4)
            self.play_card(card_index)
            
            # 等待一段时间，让能量恢复
            wait_time = random.uniform(1.5, 3.0)
            self.log(f"等待{wait_time:.1f}秒后继续操作")
            time.sleep(wait_time)
        
        # 5. 判断是否结束回合
        if gold < 2:  # 如果金币不足以进行任何操作，结束回合
            self.log("金币已用完，回合结束")
            # 实际游戏中可能需要点击回合结束按钮
            # 这里简化处理，等待一段时间
            time.sleep(3)
    
    def handle_battle_result(self):
        """
        处理战斗结果
        :return: 战斗结果描述
        """
        # 等待战斗结束画面
        result = None
        max_wait = 30  # 最多等待30秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # 检测胜利画面
            if self.find_template('victory_screen.png', confidence=0.7):
                result = "victory"
                self.log("战斗胜利！")
                break
            
            # 检测失败画面
            if self.find_template('defeat_screen.png', confidence=0.7):
                result = "defeat"
                self.log("战斗失败！")
                break
            
            # 等待一段时间再检测
            time.sleep(1)
        
        # 如果超时未检测到结果
        if result is None:
            self.log("等待战斗结果超时")
            return "timeout"
        
        # 点击确认按钮返回主界面
        time.sleep(2)  # 等待一段时间，让结算画面完全显示
        if self.click_template('ok_button.png'):
            self.log("已点击确认按钮，返回主界面")
        
        # 重置战斗状态
        self.in_battle = False
        
        return result
    
    def auto_battle_loop(self, num_battles=5, wait_between=5):
        """
        自动战斗循环
        :param num_battles: 要进行的战斗次数
        :param wait_between: 战斗之间的等待时间（秒）
        """
        self.log(f"开始自动战斗循环，计划进行 {num_battles} 次战斗")
        
        # 确保窗口处于激活状态
        if not self.activate_window():
            self.log("无法激活游戏窗口，自动战斗取消")
            return
        
        battles_completed = 0
        victories = 0
        defeats = 0
        
        try:
            while battles_completed < num_battles:
                self.log(f"开始第 {battles_completed + 1} 次战斗")
                
                # 开始战斗
                if not self.start_battle():
                    self.log("无法开始战斗，尝试重新激活窗口")
                    if not self.activate_window():
                        self.log("无法激活游戏窗口，自动战斗中断")
                        break
                    continue
                
                # 执行战斗操作，直到战斗结束
                battle_duration = 0
                max_battle_time = 180  # 最长战斗时间（秒）
                
                while self.in_battle and battle_duration < max_battle_time:
                    self.perform_battle_actions()
                    battle_duration += 3  # 假设每次操作大约3秒
                
                # 处理战斗结果
                result = self.handle_battle_result()
                battles_completed += 1
                
                if result == "victory":
                    victories += 1
                elif result == "defeat":
                    defeats += 1
                
                # 战斗之间等待一段时间
                if battles_completed < num_battles:
                    self.log(f"等待 {wait_between} 秒后开始下一场战斗")
                    time.sleep(wait_between)
            
            self.log(f"自动战斗完成，共进行 {battles_completed} 次战斗，胜利 {victories} 次，失败 {defeats} 次")
        
        except KeyboardInterrupt:
            self.log("用户中断，自动战斗停止")
        except Exception as e:
            self.log(f"发生错误: {str(e)}")
        
        return {"battles": battles_completed, "victories": victories, "defeats": defeats}