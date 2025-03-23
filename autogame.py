import cv2
import numpy as np
import pyautogui
import time
import random
import os
from datetime import datetime

# 设置pyautogui的安全特性
pyautogui.FAILSAFE = True  # 将鼠标移动到屏幕左上角将中断程序
pyautogui.PAUSE = 0.5  # 每次pyautogui操作后暂停的秒数

class AutoGame:
    def __init__(self, confidence=0.8, region=None):
        """
        初始化自动游戏类
        :param confidence: 图像匹配的置信度阈值
        :param region: 截图区域，默认为全屏
        """
        self.confidence = confidence
        self.region = region
        self.screen = None
        self.templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        
        # 确保模板目录存在
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
        
        # 日志设置
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autogame.log')
        
        print("自动游戏脚本已初始化")
    
    def log(self, message):
        """
        记录日志
        :param message: 日志消息
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def take_screenshot(self):
        """
        获取屏幕截图
        :return: 屏幕截图的numpy数组
        """
        self.screen = pyautogui.screenshot(region=self.region)
        return cv2.cvtColor(np.array(self.screen), cv2.COLOR_RGB2BGR)
    
    def find_template(self, template_name, confidence=None):
        """
        在屏幕上查找模板图像
        :param template_name: 模板图像文件名
        :param confidence: 可选的置信度覆盖
        :return: 匹配位置的中心点坐标，如果未找到则返回None
        """
        if confidence is None:
            confidence = self.confidence
            
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            self.log(f"模板文件不存在: {template_path}")
            return None
        
        screen = self.take_screenshot()
        template = cv2.imread(template_path)
        
        # 确保模板和屏幕截图都已正确加载
        if template is None:
            self.log(f"无法加载模板图像: {template_path}")
            return None
        
        # 使用OpenCV的模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            # 计算匹配区域的中心点
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            self.log(f"找到模板 {template_name} 在位置 ({center_x}, {center_y}) 置信度: {max_val:.2f}")
            return (center_x, center_y)
        else:
            self.log(f"未找到模板 {template_name} (最高置信度: {max_val:.2f})")
            return None
    
    def click(self, position, random_offset=5):
        """
        点击指定位置，可添加随机偏移以模拟人类行为
        :param position: (x, y) 坐标元组
        :param random_offset: 随机偏移的最大像素数
        """
        if position is None:
            self.log("无法点击：位置为None")
            return False
        
        x, y = position
        
        # 添加随机偏移
        if random_offset > 0:
            x += random.randint(-random_offset, random_offset)
            y += random.randint(-random_offset, random_offset)
        
        # 执行点击
        pyautogui.click(x, y)
        self.log(f"点击位置: ({x}, {y})")
        return True
    
    def click_template(self, template_name, confidence=None, random_offset=5):
        """
        查找并点击模板图像
        :param template_name: 模板图像文件名
        :param confidence: 可选的置信度覆盖
        :param random_offset: 随机偏移的最大像素数
        :return: 是否成功点击
        """
        position = self.find_template(template_name, confidence)
        return self.click(position, random_offset)
    
    def save_template(self, region, template_name):
        """
        保存指定区域的截图作为模板
        :param region: 区域元组 (left, top, width, height)
        :param template_name: 保存的模板文件名
        """
        screenshot = pyautogui.screenshot(region=region)
        template_path = os.path.join(self.templates_dir, template_name)
        screenshot.save(template_path)
        self.log(f"保存模板 {template_name} 从区域 {region}")
    
    def wait_for_template(self, template_name, max_wait=30, check_interval=1, confidence=None):
        """
        等待模板图像出现
        :param template_name: 模板图像文件名
        :param max_wait: 最大等待时间（秒）
        :param check_interval: 检查间隔（秒）
        :param confidence: 可选的置信度覆盖
        :return: 找到的位置或None
        """
        self.log(f"等待模板 {template_name} 出现，最多等待 {max_wait} 秒")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            position = self.find_template(template_name, confidence)
            if position is not None:
                return position
            time.sleep(check_interval)
        
        self.log(f"等待模板 {template_name} 超时")
        return None
    
    def detect_battle_state(self):
        """
        检测当前战斗状态
        :return: 战斗状态描述
        """
        # 这里需要根据游戏具体情况实现战斗状态检测逻辑
        # 例如检测是否在战斗中、是否可以开始战斗、战斗是否结束等
        pass
    
    def start_battle(self):
        """
        开始战斗
        :return: 是否成功开始战斗
        """
        # 点击战斗按钮
        return self.click_template('battle_button.png')
    
    def perform_battle_actions(self):
        """
        执行战斗中的操作
        """
        # 根据游戏具体情况实现战斗操作逻辑
        pass
    
    def handle_battle_result(self):
        """
        处理战斗结果
        :return: 战斗结果描述
        """
        # 根据游戏具体情况实现战斗结果处理逻辑
        pass
    
    def auto_battle_loop(self, num_battles=5, wait_between=5):
        """
        自动战斗循环
        :param num_battles: 要进行的战斗次数
        :param wait_between: 战斗之间的等待时间（秒）
        """
        self.log(f"开始自动战斗循环，计划进行 {num_battles} 次战斗")
        
        battles_completed = 0
        
        try:
            while battles_completed < num_battles:
                self.log(f"开始第 {battles_completed + 1} 次战斗")
                
                # 开始战斗
                if not self.start_battle():
                    self.log("无法开始战斗，等待后重试")
                    time.sleep(wait_between)
                    continue
                
                # 等待战斗开始
                time.sleep(2)  # 等待战斗场景加载
                
                # 执行战斗操作
                self.perform_battle_actions()
                
                # 处理战斗结果
                result = self.handle_battle_result()
                self.log(f"战斗结果: {result}")
                
                battles_completed += 1
                self.log(f"完成第 {battles_completed} 次战斗，总计划 {num_battles} 次")
                
                # 战斗间隔
                if battles_completed < num_battles:
                    self.log(f"等待 {wait_between} 秒后开始下一次战斗")
                    time.sleep(wait_between)
            
            self.log(f"自动战斗循环完成，共进行了 {battles_completed} 次战斗")
            
        except KeyboardInterrupt:
            self.log("用户中断了自动战斗循环")
        except Exception as e:
            self.log(f"自动战斗循环出错: {str(e)}")

# 示例用法
if __name__ == "__main__":
    # 创建自动游戏实例
    auto_game = AutoGame(confidence=0.7)
    
    # 给用户5秒时间切换到游戏窗口
    print("请在5秒内切换到游戏窗口...")
    time.sleep(5)
    
    # 开始自动战斗循环
    auto_game.auto_battle_loop(num_battles=3, wait_between=3)