import cv2
import numpy as np
import pyautogui
import time
import random
import os
from autogame import AutoGame

class AdvancedBattleBot(AutoGame):
    """
    高级战斗机器人，针对图像中所示的对战类游戏
    提供更多高级功能和更智能的战斗策略
    """
    def __init__(self, confidence=0.8, region=None):
        super().__init__(confidence, region)
        self.log("高级战斗机器人已初始化")
        
        # 游戏特定的状态和配置
        self.in_battle = False
        self.energy = 0  # 当前能量/法力值
        self.gold = 0  # 当前金币数量
        self.refresh_cost = 0  # 刷新卡牌消耗的金币
        self.population = 0  # 当前人口数量
        self.population_limit = 0  # 人口上限
        self.card_positions = []  # 卡牌位置
        self.opponent_units = []  # 对手单位位置
        self.ally_units = []  # 我方单位位置
        
        # 战斗区域定义（根据实际游戏调整）
        self.battle_area = None  # 将在首次截图后设置
        self.left_lane = None
        self.right_lane = None
        self.center_lane = None
        
        # 战斗策略配置
        self.aggressive_mode = True  # 是否采用激进策略
        self.card_play_order = [1, 2, 3, 4]  # 卡牌优先级
        self.target_areas = []  # 优先放置区域
        
        # 确保模板目录存在
        self.check_templates()
    
    def check_templates(self):
        """
        检查必要的模板是否存在
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
    
    def setup_battle_areas(self):
        """
        设置战斗区域坐标
        在首次截图后调用
        """
        if self.screen is None:
            self.take_screenshot()
        
        screen_width, screen_height = self.screen.size
        
        # 设置战斗区域（根据实际游戏调整）
        # 假设战斗区域在屏幕中央
        battle_width = int(screen_width * 0.8)
        battle_height = int(screen_height * 0.6)
        battle_left = (screen_width - battle_width) // 2
        battle_top = (screen_height - battle_height) // 2
        
        self.battle_area = (battle_left, battle_top, battle_width, battle_height)
        
        # 划分战斗区域为三个通道
        lane_width = battle_width // 3
        self.left_lane = (battle_left, battle_top, lane_width, battle_height)
        self.center_lane = (battle_left + lane_width, battle_top, lane_width, battle_height)
        self.right_lane = (battle_left + 2 * lane_width, battle_top, lane_width, battle_height)
        
        # 设置优先放置区域
        # 例如，在我方区域前方放置防御单位
        defense_y = battle_top + int(battle_height * 0.7)  # 靠近我方区域
        offense_y = battle_top + int(battle_height * 0.3)  # 靠近敌方区域
        
        self.target_areas = [
            # 防御位置
            (battle_left + lane_width // 2, defense_y),  # 左路防御
            (battle_left + lane_width + lane_width // 2, defense_y),  # 中路防御
            (battle_left + 2 * lane_width + lane_width // 2, defense_y),  # 右路防御
            
            # 进攻位置
            (battle_left + lane_width // 2, offense_y),  # 左路进攻
            (battle_left + lane_width + lane_width // 2, offense_y),  # 中路进攻
            (battle_left + 2 * lane_width + lane_width // 2, offense_y),  # 右路进攻
        ]
        
        self.log("战斗区域已设置")
    
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
    
    def detect_energy(self):
        """
        检测当前能量/法力值
        使用颜色识别或模板匹配
        :return: 估计的能量值(0-10)
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
        :return: 当前金币数量
        """
        # 查找金币图标位置
        gold_position = self.find_template('gold_coin.png', confidence=0.7)
        
        if not gold_position:
            self.log("无法找到金币图标")
            # 如果找不到金币图标，返回一个默认值
            return 50
        
        # 实际实现中，应该使用OCR识别金币图标旁边的数字
        # 这里使用简化版本，随机返回一个值用于测试
        self.gold = random.randint(30, 100)
        self.log(f"当前金币: {self.gold}")
        return self.gold
    
    def detect_refresh_cost(self):
        """
        检测刷新卡牌所需的金币
        :return: 刷新卡牌所需的金币
        """
        # 查找刷新卡牌按钮位置
        refresh_position = self.find_template('refresh_cards.png', confidence=0.7)
        
        if not refresh_position:
            self.log("无法找到刷新卡牌按钮")
            # 如果找不到刷新按钮，返回一个默认值
            return 2
        
        # 实际实现中，应该使用OCR识别刷新按钮上的数字
        # 这里使用简化版本，随机返回一个值用于测试
        self.refresh_cost = random.randint(1, 5)
        self.log(f"刷新卡牌消耗: {self.refresh_cost} 金币")
        return self.refresh_cost
    
    def detect_population(self):
        """
        检测当前人口数量和人口上限
        :return: (当前人口数量, 人口上限)
        """
        # 查找人口图标位置
        population_position = self.find_template('population.png', confidence=0.7)
        
        if not population_position:
            self.log("无法找到人口图标")
            # 如果找不到人口图标，返回默认值
            return (3, 6)
        
        # 实际实现中，应该使用OCR识别人口图标旁边的数字
        # 这里使用简化版本，随机返回一些值用于测试
        self.population = random.randint(1, 5)
        self.population_limit = random.randint(self.population, 10)
        self.log(f"当前人口: {self.population}/{self.population_limit}")
        return (self.population, self.population_limit)
    
    def detect_units(self):
        """
        检测场上的单位
        :return: (我方单位列表, 对手单位列表)
        """
        # 实际实现中，可以使用对象检测或颜色识别来检测场上单位
        # 这里使用简化版本
        
        # 随机生成一些单位位置用于测试
        self.ally_units = []
        self.opponent_units = []
        
        if self.battle_area is None:
            self.setup_battle_areas()
        
        battle_left, battle_top, battle_width, battle_height = self.battle_area
        
        # 随机生成1-3个我方单位
        for _ in range(random.randint(1, 3)):
            x = battle_left + random.randint(0, battle_width)
            y = battle_top + random.randint(battle_height // 2, battle_height)
            self.ally_units.append((x, y))
        
        # 随机生成1-3个敌方单位
        for _ in range(random.randint(1, 3)):
            x = battle_left + random.randint(0, battle_width)
            y = battle_top + random.randint(0, battle_height // 2)
            self.opponent_units.append((x, y))
        
        return self.ally_units, self.opponent_units
    
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
            
            # 设置战斗区域
            self.setup_battle_areas()
            
            self.in_battle = True
            return True
        elif state == "in_battle":
            self.log("已经在战斗中")
            self.in_battle = True
            return True
        else:
            self.log(f"当前状态不适合开始战斗: {state}")
            return False
    
    def select_card_to_play(self):
        """
        选择要打出的卡牌
        基于当前能量和战场状况
        :return: 卡牌索引(1-4)或None
        """
        # 检测当前能量
        energy = self.detect_energy()
        
        # 检测场上单位
        self.detect_units()
        
        # 根据战场状况选择卡牌
        # 简单策略：按照预设顺序尝试打出卡牌
        for card_idx in self.card_play_order:
            # 假设每张卡牌消耗4点能量
            if energy >= 4:
                return card_idx
        
        return None
    
    def select_target_position(self):
        """
        选择放置卡牌的目标位置
        基于战场状况和策略
        :return: 目标位置坐标
        """
        # 如果有敌方单位，优先在其附近放置
        if self.opponent_units and random.random() < 0.7:
            # 70%概率选择在敌方单位附近放置
            target = random.choice(self.opponent_units)
            # 在目标周围随机偏移一点距离
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            return (target[0] + offset_x, target[1] + offset_y)
        
        # 否则选择预设的目标区域
        if self.target_areas:
            return random.choice(self.target_areas)
        
        # 如果没有设置目标区域，在战斗区域随机选择
        if self.battle_area:
            battle_left, battle_top, battle_width, battle_height = self.battle_area
            x = battle_left + random.randint(0, battle_width)
            y = battle_top + random.randint(0, battle_height)
            return (x, y)
        
        # 默认在屏幕中央
        screen_width, screen_height = pyautogui.size()
        return (screen_width // 2, screen_height // 2)
    
    def play_card(self, card_index, target_position=None):
        """
        打出一张卡牌
        :param card_index: 卡牌索引(1-4)
        :param target_position: 目标位置，如果为None则自动选择
        :return: 是否成功打出卡牌
        """
        # 检测卡牌位置
        card_template = f'card_slot_{card_index}.png'
        card_position = self.find_template(card_template, confidence=0.6)
        
        if not card_position:
            self.log(f"找不到索引为{card_index}的卡牌")
            return False
        
        # 点击卡牌
        self.click(card_position)
        
        # 如果没有指定目标位置，则自动选择
        if target_position is None:
            target_position = self.select_target_position()
        
        # 点击目标位置放置卡牌
        time.sleep(0.5)  # 短暂延迟，模拟人类操作
        self.click(target_position)
        
        self.log(f"已打出卡牌{card_index}到位置{target_position}")
        return True
        
    def upgrade_population(self):
        """
        升级人口上限
        :return: 是否成功升级
        """
        # 检测当前人口数量和上限
        population, population_limit = self.detect_population()
        
        # 如果人口已满，尝试升级
        if population >= population_limit:
            # 查找升级人口按钮
            upgrade_position = self.find_template('upgrade_population.png', confidence=0.7)
            
            if not upgrade_position:
                self.log("找不到升级人口按钮")
                return False
            
            # 点击升级按钮
            self.click(upgrade_position)
            self.log(f"已点击升级人口按钮，人口上限从 {population_limit} 提升")
            
            # 等待升级动画完成
            time.sleep(1.0)
            
            # 重新检测人口数量和上限
            self.detect_population()
            
            return True
        else:
            self.log(f"当前人口未满 ({population}/{population_limit})，无需升级")
            return False
    
    def refresh_cards(self):
        """
        刷新卡牌
        :return: 是否成功刷新
        """
        # 检测当前金币数量和刷新消耗
        gold = self.detect_gold()
        refresh_cost = self.detect_refresh_cost()
        
        # 如果金币不足，无法刷新
        if gold < refresh_cost:
            self.log(f"金币不足，无法刷新卡牌 (需要 {refresh_cost} 金币，当前 {gold} 金币)")
            return False
        
        # 查找刷新卡牌按钮
        refresh_position = self.find_template('refresh_cards.png', confidence=0.7)
        
        if not refresh_position:
            self.log("找不到刷新卡牌按钮")
            return False
        
        # 点击刷新按钮
        self.click(refresh_position)
        self.log(f"已点击刷新卡牌按钮，消耗 {refresh_cost} 金币")
        
        # 更新金币数量
        self.gold -= refresh_cost
        self.log(f"剩余金币: {self.gold}")
        
        # 等待刷新动画完成
        time.sleep(1.0)
        
        return True
        
    def buy_card(self):
        """
        从中间三张卡牌中购买一张
        :return: 是否成功购买
        """
        # 检测当前金币数量
        gold = self.detect_gold()
        
        # 假设每张卡牌消耗3金币（实际应该从游戏中识别）
        card_cost = 3
        
        # 如果金币不足，无法购买
        if gold < card_cost:
            self.log(f"金币不足，无法购买卡牌 (需要 {card_cost} 金币，当前 {gold} 金币)")
            return False
        
        # 查找可购买的卡牌
        card_position = self.find_template('buy_card.png', confidence=0.7)
        
        if not card_position:
            self.log("找不到可购买的卡牌")
            return False
        
        # 点击卡牌进行购买
        self.click(card_position)
        self.log(f"已点击购买卡牌，消耗 {card_cost} 金币")
        
        # 更新金币数量
        self.gold -= card_cost
        self.log(f"剩余金币: {self.gold}")
        
        # 等待购买动画完成
        time.sleep(1.0)
        
        return True
    
    def merge_same_cards(self):
        """
        合并同名卡牌以升星
        :return: 是否成功合并
        """
        # 查找同名卡牌
        same_card_positions = []
        
        # 使用模板匹配查找同名卡牌
        # 这里假设已经有一个模板用于识别同名卡牌
        same_card_position = self.find_template('same_card.png', confidence=0.7)
        
        if not same_card_position:
            self.log("未找到可合并的同名卡牌")
            return False
        
        # 点击同名卡牌进行合并
        self.click(same_card_position)
        self.log("已点击同名卡牌进行合并")
        
        # 等待合并动画完成
        time.sleep(1.0)
        
        return True
    
    def perform_battle_actions(self):
        """
        执行战斗中的操作
        智能决策并执行动作
        """
        if not self.in_battle:
            self.log("当前不在战斗中，无法执行战斗操作")
            return
        
        # 检测当前能量
        energy = self.detect_energy()
        self.log(f"当前能量: {energy}")
        
        # 检测当前金币
        gold = self.detect_gold()
        
        # 检测当前人口
        population, population_limit = self.detect_population()
        
        # 检测场上单位
        ally_units, opponent_units = self.detect_units()
        self.log(f"我方单位数量: {len(ally_units)}, 敌方单位数量: {len(opponent_units)}")
        
        # 尝试合并同名卡牌升星
        if random.random() < 0.3:  # 30%概率尝试合并卡牌
            if self.merge_same_cards():
                self.log("成功合并同名卡牌升星")
                # 合并后等待一段时间
                time.sleep(1.0)
                return
        
        # 尝试升级人口
        # 当人口接近上限时，优先考虑升级人口
        if population >= population_limit - 1:
            if self.upgrade_population():
                self.log("成功升级人口上限")
                # 升级后等待一段时间
                time.sleep(1.0)
                return
        
        # 尝试购买卡牌
        # 当金币充足且人口未满时，优先考虑购买卡牌
        if gold >= 3 and population < population_limit:
            if random.random() < 0.4:  # 40%概率尝试购买卡牌
                if self.buy_card():
                    self.log("成功购买卡牌")
                    # 购买后等待一段时间
                    time.sleep(1.0)
                    return
        
        # 尝试刷新卡牌
        # 当金币充足且没有合适的卡牌时，考虑刷新
        refresh_cost = self.detect_refresh_cost()
        if gold >= refresh_cost * 2:  # 确保刷新后仍有足够金币购买卡牌
            if random.random() < 0.25:  # 25%概率尝试刷新卡牌
                if self.refresh_cards():
                    self.log("成功刷新卡牌")
                    # 刷新后等待一段时间
                    time.sleep(1.0)
                    return
        
        # 根据战场状况选择策略
        if len(opponent_units) > len(ally_units) and len(opponent_units) >= 2:
            # 敌方单位较多，采用防御策略
            self.log("敌方单位较多，采用防御策略")
            self.aggressive_mode = False
        elif energy >= 8:  # 能量充足，采用进攻策略
            self.log("能量充足，采用进攻策略")
            self.aggressive_mode = True
        
        # 选择要打出的卡牌
        card_to_play = self.select_card_to_play()
        
        if card_to_play:
            # 根据当前策略选择目标位置
            if self.aggressive_mode:
                # 进攻策略，优先选择靠近敌方的位置
                target_areas = self.target_areas[3:] if self.target_areas else None
                target_position = random.choice(target_areas) if target_areas else None
            else:
                # 防御策略，优先选择靠近我方的位置
                target_areas = self.target_areas[:3] if self.target_areas else None
                target_position = random.choice(target_areas) if target_areas else None
            
            # 打出卡牌
            self.play_card(card_to_play, target_position)
            
            # 等待一段时间，让能量恢复
            wait_time = random.uniform(1.5, 3.0)
            self.log(f"等待{wait_time:.1f}秒后继续操作")
            time.sleep(wait_time)
    
    def handle_battle_result(self):
        """
        处理战斗结果
        :return: 战斗结果描述
        """
        # 检测战斗结果
        state = self.detect_battle_state()
        
        if state == "victory":
            self.log("战斗胜利！")
            # 点击确认按钮
            if self.click_template('ok_button.png'):
                self.log("已确认胜利")
            else:
                self.log("无法找到确认按钮，尝试点击屏幕中央")
                # 如果找不到确认按钮，尝试点击屏幕中央
                screen_width, screen_height = pyautogui.size()
                self.click((screen_width // 2, screen_height // 2))
            
            self.in_battle = False
            return "victory"
        
        elif state == "defeat":
            self.log("战斗失败！")
            # 点击确认按钮
            if self.click_template('ok_button.png'):
                self.log("已确认失败")
            else:
                self.log("无法找到确认按钮，尝试点击屏幕中央")
                # 如果找不到确认按钮，尝试点击屏幕中央
                screen_width, screen_height = pyautogui.size()
                self.click((screen_width // 2, screen_height // 2))
            
            self.in_battle = False
            return "defeat"
        
        elif state == "in_battle":
            self.log("战斗仍在进行中")
            return "in_battle"
        
        else:
            self.log(f"未知状态: {state}")
            return "unknown"
    
    def auto_battle_loop(self, num_battles=5, wait_between=5):
        """
        自动战斗循环
        :param num_battles: 要进行的战斗次数
        :param wait_between: 战斗之间的等待时间（秒）
        """
        self.log(f"开始自动战斗循环，计划进行 {num_battles} 次战斗")
        
        battles_completed = 0
        victories = 0
        defeats = 0
        
        try:
            while battles_completed < num_battles:
                self.log(f"\n===== 开始第 {battles_completed + 1} 场战斗 =====")
                
                # 开始战斗
                if not self.start_battle():
                    self.log("无法开始战斗，等待后重试")
                    time.sleep(wait_between)
                    continue
                
                # 战斗中的操作循环
                battle_time = 0
                max_battle_time = 180  # 最长战斗时间（秒）
                check_interval = 2  # 检查间隔（秒）
                
                while battle_time < max_battle_time:
                    # 检查战斗是否结束
                    state = self.detect_battle_state()
                    if state in ["victory", "defeat"]:
                        break
                    
                    # 执行战斗操作
                    self.perform_battle_actions()
                    
                    # 等待一段时间
                    time.sleep(check_interval)
                    battle_time += check_interval
                
                # 处理战斗结果
                result = self.handle_battle_result()
                
                if result == "victory":
                    victories += 1
                elif result == "defeat":
                    defeats += 1
                
                battles_completed += 1
                
                # 战斗间等待
                if battles_completed < num_battles:
                    self.log(f"等待 {wait_between} 秒后开始下一场战斗")
                    time.sleep(wait_between)
            
            self.log(f"\n===== 战斗循环结束 =====")
            self.log(f"总场次: {battles_completed}, 胜利: {victories}, 失败: {defeats}")
            self.log(f"胜率: {victories / battles_completed * 100:.1f}%")
            
        except KeyboardInterrupt:
            self.log("\n用户中断，停止战斗循环")
            self.log(f"已完成场次: {battles_completed}, 胜利: {victories}, 失败: {defeats}")
            if battles_completed > 0:
                self.log(f"胜率: {victories / battles_completed * 100:.1f}%")


def main():
    """
    主函数
    """
    print("===== 高级战斗机器人 =====")
    print("初始化中...")
    
    # 创建机器人实例
    bot = AdvancedBattleBot(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 开始自动战斗循环
    num_battles = 3
    try:
        num_battles = int(input("请输入要进行的战斗次数: "))
    except ValueError:
        print("输入无效，使用默认值3")
    
    bot.auto_battle_loop(num_battles=num_battles)


if __name__ == "__main__":
    main()")
        
        # 检测场上单位
        ally_units, opponent_units = self.detect_units()
        self.log(f"我方单位数量: {len(ally_units)}, 敌方单位数量: {len(opponent_units)}")
        
        # 根据战场状况选择策略
        if len(opponent_units) > len(ally_units) and len(opponent_units) >= 2:
            # 敌方单位较多，采用防御策略
            self.log("敌方单位较多，采用防御策略")
            self.aggressive_mode = False
        elif energy >= 8:  # 能量充足，采用进攻策略
            self.log("能量充足，采用进攻策略")
            self.aggressive_mode = True
        
        # 选择要打出的卡牌
        card_to_play = self.select_card_to_play()
        
        if card_to_play:
            # 根据当前策略选择目标位置
            if self.aggressive_mode:
                # 进攻策略，优先选择靠近敌方的位置
                target_areas = self.target_areas[3:] if self.target_areas else None
                target_position = random.choice(target_areas) if target_areas else None
            else:
                # 防御策略，优先选择靠近我方的位置
                target_areas = self.target_areas[:3] if self.target_areas else None
                target_position = random.choice(target_areas) if target_areas else None
            
            # 打出卡牌
            self.play_card(card_to_play, target_position)
            
            # 等待一段时间，让能量恢复
            wait_time = random.uniform(1.5, 3.0)
            self.log(f"等待{wait_time:.1f}秒后继续操作")
            time.sleep(wait_time)
    
    def handle_battle_result(self):
        """
        处理战斗结果
        :return: 战斗结果描述
        """
        # 检测战斗结果
        state = self.detect_battle_state()
        
        if state == "victory":
            self.log("战斗胜利！")
            # 点击确认按钮
            if self.click_template('ok_button.png'):
                self.log("已确认胜利")
            else:
                self.log("无法找到确认按钮，尝试点击屏幕中央")
                # 如果找不到确认按钮，尝试点击屏幕中央
                screen_width, screen_height = pyautogui.size()
                self.click((screen_width // 2, screen_height // 2))
            
            self.in_battle = False
            return "victory"
        
        elif state == "defeat":
            self.log("战斗失败！")
            # 点击确认按钮
            if self.click_template('ok_button.png'):
                self.log("已确认失败")
            else:
                self.log("无法找到确认按钮，尝试点击屏幕中央")
                # 如果找不到确认按钮，尝试点击屏幕中央
                screen_width, screen_height = pyautogui.size()
                self.click((screen_width // 2, screen_height // 2))
            
            self.in_battle = False
            return "defeat"
        
        elif state == "in_battle":
            self.log("战斗仍在进行中")
            return "in_battle"
        
        else:
            self.log(f"未知状态: {state}")
            return "unknown"
    
    def auto_battle_loop(self, num_battles=5, wait_between=5):
        """
        自动战斗循环
        :param num_battles: 要进行的战斗次数
        :param wait_between: 战斗之间的等待时间（秒）
        """
        self.log(f"开始自动战斗循环，计划进行 {num_battles} 次战斗")
        
        battles_completed = 0
        victories = 0
        defeats = 0
        
        try:
            while battles_completed < num_battles:
                self.log(f"\n===== 开始第 {battles_completed + 1} 场战斗 =====")
                
                # 开始战斗
                if not self.start_battle():
                    self.log("无法开始战斗，等待后重试")
                    time.sleep(wait_between)
                    continue
                
                # 战斗中的操作循环
                battle_time = 0
                max_battle_time = 180  # 最长战斗时间（秒）
                check_interval = 2  # 检查间隔（秒）
                
                while battle_time < max_battle_time:
                    # 检查战斗是否结束
                    state = self.detect_battle_state()
                    if state in ["victory", "defeat"]:
                        break
                    
                    # 执行战斗操作
                    self.perform_battle_actions()
                    
                    # 等待一段时间
                    time.sleep(check_interval)
                    battle_time += check_interval
                
                # 处理战斗结果
                result = self.handle_battle_result()
                
                if result == "victory":
                    victories += 1
                elif result == "defeat":
                    defeats += 1
                
                battles_completed += 1
                
                # 战斗间等待
                if battles_completed < num_battles:
                    self.log(f"等待 {wait_between} 秒后开始下一场战斗")
                    time.sleep(wait_between)
            
            self.log(f"\n===== 战斗循环结束 =====")
            self.log(f"总场次: {battles_completed}, 胜利: {victories}, 失败: {defeats}")
            self.log(f"胜率: {victories / battles_completed * 100:.1f}%")
            
        except KeyboardInterrupt:
            self.log("\n用户中断，停止战斗循环")
            self.log(f"已完成场次: {battles_completed}, 胜利: {victories}, 失败: {defeats}")
            if battles_completed > 0:
                self.log(f"胜率: {victories / battles_completed * 100:.1f}%")


def main():
    """
    主函数
    """
    print("===== 高级战斗机器人 =====")
    print("初始化中...")
    
    # 创建机器人实例
    bot = AdvancedBattleBot(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 开始自动战斗循环
    num_battles = 3
    try:
        num_battles = int(input("请输入要进行的战斗次数: "))
    except ValueError:
        print("输入无效，使用默认值3")
    
    bot.auto_battle_loop(num_battles=num_battles)


if __name__ == "__main__":
    main()