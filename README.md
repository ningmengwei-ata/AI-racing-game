# AI Racing Game README
## 项目简介
AI赛车避障游戏基于Pygame开发，包含`game_util.py`和`main_game.py`两个核心文件，实现AI自动避障、多关卡难度动态调整的赛车游戏。

## 核心文件说明
1. **game_util.py**：提供辅助功能，包含颜色选择界面绘制、通关/游戏结束弹窗渲染等UI相关函数，为游戏提供可视化交互支持。
2. **main_game.py**：游戏主逻辑文件，实现赛车控制（左右箭头手动/AI自动）、障碍物生成、关卡难度动态调整（速度/危险距离/生成频率）、AI避障决策（基于车道安全分数选最优车道）等核心功能，支持自动重启、操作说明自动/手动跳转。

## 操作说明
- 左右箭头：手动调整赛车方向
- Enter键：跳过操作说明/重启游戏
- 通关条件：达到当前关卡目标分数，碰撞障碍物则游戏结束。


The AI Racing Obstacle Avoidance Game is developed based on Pygame, consisting of two core files: `game_util.py` and `main_game.py`. It implements a racing game with AI automatic obstacle avoidance and dynamic difficulty adjustment across multiple levels.  

### Core File Explanation
1. `game_util.py`: Provides auxiliary functions, including drawing the color selection interface and rendering pop-ups for level completion/game over, supporting visual interactive elements of the game.  
2. `main_game.py`: The core logic file, implementing car control (arrow keys for manual/AI for automatic), obstacle generation, dynamic level difficulty adjustment (speed/danger distance/spawn rate), and AI obstacle avoidance decision-making (selecting the optimal lane based on lane safety scores).  

### Operation Instructions
- Left/Right Arrows: Manually adjust the car's direction  
- Enter Key: Skip operation tips / restart the game  
- Clear Condition: Reach the target score of the current level; collision with obstacles ends the game.  

