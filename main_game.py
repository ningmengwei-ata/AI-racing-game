import pygame
import random
import sys
from game_util import draw_color_selection, show_level_pass_popup, show_game_over_popup, COLOR_OPTIONS

# 游戏基础配置
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
LANE_COUNT = 3
LANE_WIDTH = SCREEN_WIDTH // LANE_COUNT

# 基础颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# 字体
FONT = pygame.font.Font(None, 40)
SCORE_FONT = pygame.font.Font(None, 30)
TIPS_FONT = pygame.font.Font(None, 25)
COUNTDOWN_FONT = pygame.font.Font(None, 30)

class RacingGame:
    # 可选参数current_level，默认1
    def __init__(self, car_color, current_level=1):
        # 游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI 赛车避障")
        self.clock = pygame.time.Clock()
        
        # 赛车属性（自定义颜色）
        self.car_color = car_color
        self.car_width = LANE_WIDTH - 10
        self.car_height = 80
        self.current_lane = 1
        self.car_x = self.get_lane_center_x(self.current_lane)
        self.car_y = SCREEN_HEIGHT - self.car_height - 20
        self.car_speed = 15
        
        # 障碍物属性（按关卡动态调整）
        self.obstacles = []
        self.obstacle_width = self.car_width
        self.obstacle_height = 60
        # 核心修改2：使用传入的关卡数，而非固定1
        self.current_level = current_level  
        # 动态难度参数（基于传入的关卡数计算）
        self.base_obstacle_speed = 8 + (self.current_level - 1)
        self.base_spawn_rate = 40 - 5 * (self.current_level - 1)
        self.obstacle_speed = self.base_obstacle_speed
        self.obstacle_spawn_rate = max(self.base_spawn_rate, 20)
        
        # AI决策参数
        self.change_lane_cooldown = 0
        self.COOLDOWN_FRAMES = 30
        # 规则：第1关400px → 每升1关减少30px → 下限150px（避免过小）
        self.DANGER_DISTANCE = max(150, 400 - 30 * (self.current_level - 1))
        
        # 关卡分数系统（基于传入的关卡数计算）
        self.score = 0
        self.level_pass_score = 60 + 20 * (self.current_level - 1)
        self.game_over = False
        self.pass_level = False
        self.frame_count = 0

    def get_lane_center_x(self, lane):
        """计算车道中心x坐标"""
        lane_start_x = lane * LANE_WIDTH
        return lane_start_x + (LANE_WIDTH // 2) - (self.car_width // 2)

    def draw_road(self):
        """绘制道路"""
        self.screen.fill(GRAY)
        # 车道线
        for i in range(1, LANE_COUNT):
            x = i * LANE_WIDTH
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.rect(self.screen, WHITE, (x - 3, y, 6, 20))

    def draw_car(self):
        """绘制自定义颜色的赛车"""
        # 赛车主体
        pygame.draw.rect(self.screen, self.car_color, (self.car_x, self.car_y, self.car_width, self.car_height), border_radius=8)
        # 车轮（黑色）
        wheel_radius = 10
        wheel_pos = [
            (self.car_x + 15, self.car_y + self.car_height),
            (self.car_x + self.car_width - 15, self.car_y + self.car_height),
            (self.car_x + 15, self.car_y),
            (self.car_x + self.car_width - 15, self.car_y)
        ]
        for pos in wheel_pos:
            pygame.draw.circle(self.screen, BLACK, pos, wheel_radius)

    def spawn_obstacle(self):
        """生成障碍物"""
        lane = random.randint(0, LANE_COUNT - 1)
        obstacle_x = self.get_lane_center_x(lane)
        self.obstacles.append({
            'x': obstacle_x,
            'y': -self.obstacle_height,
            'width': self.obstacle_width,
            'height': self.obstacle_height,
            'lane': lane
        })

    def move_obstacles(self):
        """移动障碍物并更新分数"""
        new_obstacles = []
        for obs in self.obstacles:
            obs['y'] += self.obstacle_speed
            if obs['y'] < SCREEN_HEIGHT:
                new_obstacles.append(obs)
            else:
                self.score += 1
        self.obstacles = new_obstacles

    def draw_obstacles(self):
        """绘制障碍物"""
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, RED, (obs['x'], obs['y'], obs['width'], obs['height']), border_radius=5)
            pygame.draw.rect(self.screen, BLACK, (obs['x']+10, obs['y']+10, obs['width']-20, 10))

    def check_collision(self):
        """碰撞检测"""
        car_rect = pygame.Rect(self.car_x, self.car_y, self.car_width, self.car_height)
        for obs in self.obstacles:
            obs_rect = pygame.Rect(obs['x'], obs['y'], obs['width'], obs['height'])
            if car_rect.colliderect(obs_rect):
                self.game_over = True
                return True
        return False

    def calculate_lane_safety(self):
        """计算车道安全分数（仅前方障碍物）"""
        lane_scores = {0: 100, 1: 100, 2: 100}
        car_top_y = self.car_y
        
        for obs in self.obstacles:
            lane = obs['lane']
            obs_bottom_y = obs['y'] + obs['height']
            
            if obs_bottom_y < car_top_y + self.car_height and obs['y'] < car_top_y:
                distance = car_top_y - obs_bottom_y
                if 0 <= distance < self.DANGER_DISTANCE:
                    if distance < 100:
                        lane_scores[lane] = 0
                    else:
                        lane_scores[lane] = distance
        return lane_scores

    def ai_control(self):
        """AI避障逻辑"""
        if self.game_over or self.pass_level:
            return
        
        if self.change_lane_cooldown > 0:
            self.change_lane_cooldown -= 1
            return
        
        lane_scores = self.calculate_lane_safety()
        safe_lanes = [(lane, score) for lane, score in lane_scores.items() if score > 0]
        
        if not safe_lanes:
            return
        
        if (self.current_lane, lane_scores[self.current_lane]) in safe_lanes:
            best_lane = self.current_lane
        else:
            safe_lanes.sort(key=lambda x: x[1], reverse=True)
            best_lane = safe_lanes[0][0]
        
        if best_lane != self.current_lane:
            self.current_lane = best_lane
            self.change_lane_cooldown = self.COOLDOWN_FRAMES
        
        self.car_x = self.get_lane_center_x(self.current_lane)

    def update_level_difficulty(self):
        """动态调整难度"""
        self.current_level += 1
        self.level_pass_score = 60 + 20 * (self.current_level - 1)
        self.base_obstacle_speed = min(8 + (self.current_level - 1), 20)
        self.obstacle_speed = self.base_obstacle_speed
        self.base_spawn_rate = 40 - 5 * (self.current_level - 1)
        self.obstacle_spawn_rate = max(self.base_spawn_rate, 20)
        self.pass_level = False
        self.score = 0
        self.obstacles = []

    def draw_ui(self):
        """顶部UI排版"""
        pygame.draw.rect(self.screen, (180, 180, 180), (0, 0, SCREEN_WIDTH, 50))
        
        score_text = SCORE_FONT.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        level_text = SCORE_FONT.render(f"Level: {self.current_level}", True, BLACK)
        self.screen.blit(level_text, (110, 10))
        
        target_text = SCORE_FONT.render(f"Target: {self.level_pass_score}", True, BLACK)
        self.screen.blit(target_text, (190, 10))
        
        speed_text = SCORE_FONT.render(f"Speed: {int(self.obstacle_speed)}", True, BLACK)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 100, 10))

    #run_game_loop返回当前关卡数
    def run_game_loop(self):
        """游戏主循环"""
        running = True
        continue_btn_rect = None
        restart_btn_rect = None
        self.waiting_for_input = False
        
        while running:
            self.clock.tick(FPS)
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    # 返回：是否重启 + 当前关卡（退出游戏则返回False+0）
                    return (False, 0)
                
                # 通关弹窗点击 Next Level
                if event.type == pygame.MOUSEBUTTONDOWN and self.pass_level and self.waiting_for_input:
                    if continue_btn_rect and continue_btn_rect.collidepoint(event.pos):
                        self.update_level_difficulty()
                        continue_btn_rect = None
                        self.waiting_for_input = False
                
                # 游戏结束弹窗点击 Restart
                if event.type == pygame.MOUSEBUTTONDOWN and self.game_over and self.waiting_for_input:
                    if restart_btn_rect and restart_btn_rect.collidepoint(event.pos):
                        running = False
                        # 返回：是否重启 + 当前关卡（重启则返回True+当前关卡）
                        return (True, self.current_level)
                
                # 键盘触发弹窗操作
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.pass_level and self.waiting_for_input:
                        self.update_level_difficulty()
                        self.waiting_for_input = False
                    if event.key == pygame.K_RETURN and self.game_over and self.waiting_for_input:
                        running = False
                        # 返回：是否重启 + 当前关卡
                        return (True, self.current_level)
                
                # 手动控制车道（左右箭头）
                if event.type == pygame.KEYDOWN and not self.game_over and not self.pass_level and not self.waiting_for_input:
                    if event.key == pygame.K_LEFT and self.current_lane > 0:
                        self.current_lane -= 1
                        self.car_x = self.get_lane_center_x(self.current_lane)
                        self.change_lane_cooldown = self.COOLDOWN_FRAMES
                    elif event.key == pygame.K_RIGHT and self.current_lane < LANE_COUNT - 1:
                        self.current_lane += 1
                        self.car_x = self.get_lane_center_x(self.current_lane)
                        self.change_lane_cooldown = self.COOLDOWN_FRAMES

            # 游戏逻辑（仅非等待状态执行）
            if not self.game_over and not self.pass_level and not self.waiting_for_input:
                self.frame_count += 1
                if self.frame_count % self.obstacle_spawn_rate == 0:
                    self.spawn_obstacle()
                    self.frame_count = 0
                
                self.move_obstacles()
                self.ai_control()
                collision = self.check_collision()
                if collision:
                    self.waiting_for_input = True

                if self.score >= self.level_pass_score:
                    self.pass_level = True
                    self.waiting_for_input = True

            # 绘制游戏画面
            self.draw_road()
            self.draw_car()
            self.draw_obstacles()
            self.draw_ui()

            # 显示通关弹窗
            if self.pass_level and not continue_btn_rect and self.waiting_for_input:
                continue_btn_rect = show_level_pass_popup(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT, self.current_level, self.score)
                pygame.display.flip()
            # 显示游戏结束弹窗
            if self.game_over and not restart_btn_rect and self.waiting_for_input:
                restart_btn_rect = show_game_over_popup(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT, self.score, self.current_level)
                pygame.display.flip()

            # 正常游戏画面刷新
            if not self.waiting_for_input:
                pygame.display.flip()

        # 兜底返回：不重启 + 0关卡
        return (False, 0)

# 操作说明界面函数（
def show_operation_tips(screen, width, height):
    """显示操作说明界面（支持自动跳转+手动跳过）"""
    # 初始化倒计时（6秒）
    countdown = 6
    start_ticks = pygame.time.get_ticks()
    running = True
    
    while running:
        # 计算剩余时间
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        remaining_time = max(0, countdown - int(elapsed_time))
        
        # 绘制背景
        screen.fill((240, 240, 240))
        
        # 标题
        title = FONT.render("Game Operation", True, BLACK)
        screen.blit(title, (width//2 - title.get_width()//2, 50))
        
        # 操作说明列表
        tips = [
            "<- -> : Move the car left/right",
            "AI Auto-dodge obstacles",
            "Reach target score to pass level",
            "Avoid collision with obstacles"
        ]
        start_y = 150
        for i, tip in enumerate(tips):
            tip_text = TIPS_FONT.render(tip, True, BLACK)
            screen.blit(tip_text, (width//2 - tip_text.get_width()//2, start_y + i*40))
        
        # 倒计时提示
        if remaining_time > 0:
            countdown_text = COUNTDOWN_FONT.render(f"Start in {int(remaining_time)}s (Press Enter to skip)", True, GREEN)
        else:
            countdown_text = COUNTDOWN_FONT.render("Press Enter to start", True, GREEN)
        screen.blit(countdown_text, (width//2 - countdown_text.get_width()//2, height - 120))  
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 手动跳过：仅Enter键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False
        
        # 自动跳转：倒计时结束
        if remaining_time <= 0:
            running = False
        
        pygame.display.flip()

def main():
    """主程序入口（核心修改：传递当前关卡数）"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # 初始化当前关卡变量
    current_game_level = 1  

    while True:
        # 颜色选择阶段
        selected_color_idx = 0
        color_selected = False
        car_color = (0, 0, 255)
        color_btn_rects = []
        confirm_btn_rect = None

        while not color_selected:
            clock.tick(FPS)
            car_color_name, car_color, color_btn_rects, confirm_btn_rect = draw_color_selection(
                screen, SCREEN_WIDTH, SCREEN_HEIGHT, selected_color_idx
            )
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_color_idx = max(0, selected_color_idx - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_color_idx = min(len(COLOR_OPTIONS)-1, selected_color_idx + 1)
                    elif event.key == pygame.K_RETURN:
                        color_selected = True
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for idx, rect in enumerate(color_btn_rects):
                        if rect.collidepoint(mouse_x, mouse_y):
                            selected_color_idx = idx
                    if confirm_btn_rect and confirm_btn_rect.collidepoint(mouse_x, mouse_y):
                        color_selected = True

        # 显示操作说明界面
        show_operation_tips(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # 启动游戏时传入当前关卡数
        game = RacingGame(car_color, current_game_level)
        # 接收返回值：是否重启 + 重启后的关卡数
        restart, new_level = game.run_game_loop()
        
        if restart:
            # 重启时更新当前关卡数（保持失败时的关卡）
            current_game_level = new_level
        else:
            # 不重启则退出循环
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()