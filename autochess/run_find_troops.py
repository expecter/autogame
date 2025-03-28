import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入寻找野怪部队工具
from template_tools.find_troops import find_troops_main

if __name__ == "__main__":
    find_troops_main()