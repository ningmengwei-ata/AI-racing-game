import pygame

pygame.font.init()

# 颜色配置
COLOR_OPTIONS = {
    "Blue": (0, 0, 139),
    "Green": (0, 100, 0),
    "Purple": (128, 0, 128),
    "Orange": (255, 165, 0)
}

# 字体配置
TITLE_FONT = pygame.font.Font(None, 30)  
BTN_FONT = pygame.font.Font(None, 30)    
TEXT_FONT = pygame.font.Font(None, 20)   

def draw_color_selection(screen, screen_width, screen_height, selected_color_idx):
    """修复版：颜色选择界面（返回按钮坐标用于交互判断）"""
    screen.fill((200, 200, 200))  # 浅灰色背景
    
    # 标题（换行显示+居中）
    title_line1 = TITLE_FONT.render("Choose the color", True, (0, 0, 0))
    title_line2 = TITLE_FONT.render("of your race car", True, (0, 0, 0))
    line1_x = screen_width // 2 - title_line1.get_width() // 2
    line2_x = screen_width // 2 - title_line2.get_width() // 2
    screen.blit(title_line1, (line1_x, 30))
    screen.blit(title_line2, (line2_x, 70))
    
    # 颜色选项按钮
    color_names = list(COLOR_OPTIONS.keys())
    btn_width = 200
    btn_height = 50
    start_y = 130
    gap = 15
    color_btn_rects = []  # 存储颜色按钮的矩形坐标（用于点击判断）
    
    for idx, name in enumerate(color_names):
        x = screen_width // 2 - btn_width // 2
        y = start_y + idx * (btn_height + gap)
        btn_rect = pygame.Rect(x, y, btn_width, btn_height)
        color_btn_rects.append(btn_rect)
        
        # 选中状态高亮边框
        if idx == selected_color_idx:
            pygame.draw.rect(screen, (0, 0, 0), (x-5, y-5, btn_width+10, btn_height+10), border_radius=8)
        
        # 按钮背景
        pygame.draw.rect(screen, COLOR_OPTIONS[name], btn_rect, border_radius=8)
        
        # 按钮文字
        text = BTN_FONT.render(name, True, (255, 255, 255))
        text_x = x + btn_width // 2 - text.get_width() // 2
        text_y = y + btn_height // 2 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))
    
    # 确认按钮
    confirm_btn_width = 200
    confirm_btn_height = 60
    confirm_btn_x = screen_width // 2 - confirm_btn_width // 2
    confirm_btn_y = start_y + len(color_names) * (btn_height + gap) + 20
    confirm_btn_rect = pygame.Rect(confirm_btn_x, confirm_btn_y, confirm_btn_width, confirm_btn_height)
    
    pygame.draw.rect(screen, (20, 180, 20), confirm_btn_rect, border_radius=8)
    confirm_text = BTN_FONT.render("Confirm", True, (255, 255, 255))
    confirm_text_x = confirm_btn_x + confirm_btn_width // 2 - confirm_text.get_width() // 2
    confirm_text_y = confirm_btn_y + confirm_btn_height // 2 - confirm_text.get_height() // 2
    screen.blit(confirm_text, (confirm_text_x, confirm_text_y))
    
    pygame.display.flip()
    # 返回：选中颜色名、颜色值、颜色按钮矩形列表、确认按钮矩形
    return (color_names[selected_color_idx], 
            COLOR_OPTIONS[color_names[selected_color_idx]],
            color_btn_rects,
            confirm_btn_rect)

def show_level_pass_popup(screen, screen_width, screen_height, current_level, score):
    """修复版：通关弹窗（强制刷新+确保按钮坐标正确返回）"""
    # 1. 先清空屏幕，避免弹窗被覆盖（核心修复）
    screen.fill((0, 0, 0))
    
    # 半透明遮罩
    mask = pygame.Surface((screen_width, screen_height))
    mask.set_alpha(180)
    mask.fill((0, 0, 0))
    screen.blit(mask, (0, 0))
    
    # 弹窗主体（增加边框，更醒目）
    popup_width = 300
    popup_height = 200
    popup_x = screen_width//2 - popup_width//2
    popup_y = screen_height//2 - popup_height//2
    # 外层黑色边框
    pygame.draw.rect(screen, (0, 0, 0), (popup_x-3, popup_y-3, popup_width+6, popup_height+6), border_radius=10)
    # 内层白色背景
    pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), border_radius=10)
    
    # 通关文字（修正中文感叹号为英文，避免显示异常）
    pass_text = TITLE_FONT.render("Congratulations!", True, (0, 200, 0))
    screen.blit(pass_text, (popup_x + 150 - pass_text.get_width()//2, popup_y + 30))
    
    # 关卡/分数信息（调整位置，更居中）
    level_text = TEXT_FONT.render(f"Level {current_level} Completed", True, (0, 0, 0))
    screen.blit(level_text, (popup_x + 150 - level_text.get_width()//2, popup_y + 80))
    
    score_text = TEXT_FONT.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (popup_x + 150 - score_text.get_width()//2, popup_y + 110))
    
    # 继续按钮（调整尺寸+位置，确保点击区域准确）
    continue_btn_x = popup_x + 50
    continue_btn_y = popup_y + 140
    continue_btn_rect = pygame.Rect(continue_btn_x, continue_btn_y, 200, 50)
    # 按钮高亮边框
    pygame.draw.rect(screen, (0, 150, 0), (continue_btn_x-2, continue_btn_y-2, 204, 54), border_radius=8)
    pygame.draw.rect(screen, (0, 200, 0), continue_btn_rect, border_radius=8)
    
    continue_text = BTN_FONT.render("Next Level", True, (255, 255, 255))
    screen.blit(continue_text, (continue_btn_x + 100 - continue_text.get_width()//2, 
                                continue_btn_y + 25 - continue_text.get_height()//2))
    
    # 2. 强制刷新屏幕（核心修复：确保弹窗立即显示）
    pygame.display.flip()
    # 3. 暂停10ms，避免主循环过快覆盖弹窗
    pygame.time.delay(10)
    
    return continue_btn_rect

def show_game_over_popup(screen, screen_width, screen_height, final_score, max_level):
    """修复版：游戏结束弹窗（强制刷新+确保按钮坐标正确返回）"""
    # 1. 先清空屏幕，避免弹窗被覆盖（核心修复）
    screen.fill((0, 0, 0))
    
    # 半透明遮罩
    mask = pygame.Surface((screen_width, screen_height))
    mask.set_alpha(180)
    mask.fill((0, 0, 0))
    screen.blit(mask, (0, 0))
    
    # 弹窗主体（增加边框，更醒目）
    popup_width = 300
    popup_height = 220
    popup_x = screen_width//2 - popup_width//2
    popup_y = screen_height//2 - popup_height//2
    # 外层黑色边框
    pygame.draw.rect(screen, (0, 0, 0), (popup_x-3, popup_y-3, popup_width+6, popup_height+6), border_radius=10)
    # 内层白色背景
    pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), border_radius=10)
    
    # 游戏结束文字
    over_text = TITLE_FONT.render("Game Over", True, (255, 0, 0))
    screen.blit(over_text, (popup_x + 150 - over_text.get_width()//2, popup_y + 20))
    
    # 分数/关卡信息（调整位置，更居中）
    score_text = TEXT_FONT.render(f"Final Score: {final_score}", True, (0, 0, 0))
    screen.blit(score_text, (popup_x + 150 - score_text.get_width()//2, popup_y + 70))
    
    level_text = TEXT_FONT.render(f"Highest Level: {max_level}", True, (0, 0, 0))
    screen.blit(level_text, (popup_x + 150 - level_text.get_width()//2, popup_y + 100))
    
    # 重启按钮（调整尺寸+位置，确保点击区域准确）
    restart_btn_x = popup_x + 50
    restart_btn_y = popup_y + 140
    restart_btn_rect = pygame.Rect(restart_btn_x, restart_btn_y, 200, 50)
    # 按钮高亮边框
    pygame.draw.rect(screen, (200, 0, 0), (restart_btn_x-2, restart_btn_y-2, 204, 54), border_radius=8)
    pygame.draw.rect(screen, (255, 0, 0), restart_btn_rect, border_radius=8)
    
    restart_text = BTN_FONT.render("Restart", True, (255, 255, 255))
    screen.blit(restart_text, (restart_btn_x + 100 - restart_text.get_width()//2, 
                               restart_btn_y + 25 - restart_text.get_height()//2))
    
    # 2. 强制刷新屏幕（核心修复：确保弹窗立即显示）
    pygame.display.flip()
    # 3. 暂停10ms，避免主循环过快覆盖弹窗
    pygame.time.delay(10)
    
    return restart_btn_rect