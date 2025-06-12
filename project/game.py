import pygame
import sys
import random
import time
import os

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Армрестлинг")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 60, 120)
LIGHT_BLUE = (70, 130, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# Шрифты
font_large = pygame.font.SysFont('Arial', 72, bold=True)
font_medium = pygame.font.SysFont('Arial', 48)
font_small = pygame.font.SysFont('Arial', 24)

# Создание синего фона
def create_blue_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color = (30, 60 + y // 4, 120 + y // 8)
        pygame.draw.line(background, color, (0, y), (WIDTH, y))
    return background

blue_background = create_blue_background()

# Загрузка 3 кадров анимации
def load_animation_frames():
    frames = {}
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for i in range(1,10):  
        try:
            image_path = os.path.join(base_path, f"picture/{i}.png")
            image = pygame.image.load(image_path)
            frames[i] = pygame.transform.scale(image, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Ошибка загрузки кадра {i}: {e}")
            frames[i] = create_blue_background()
    
    return frames

animation_frames = load_animation_frames()
current_frame = 5  # Начальный кадр

# Уровни игры
levels = [
    {"name": "Уровень 1", "key_time": 1.0, "miss_limit": 4},
    {"name": "Уровень 2", "key_time": 0.75, "miss_limit": 4},
    {"name": "Уровень 3", "key_time": 0.5, "miss_limit": 4}
]

# Игровые состояния
MENU = 0
LEVEL_PREVIEW = 1
COUNTDOWN = 2
GAME = 3
RESULT = 4

# Игровые переменные
game_state = MENU
selected_level = 0
current_key = None
score = 0
miss_count = 0
start_time = 0
countdown = 2
last_countdown_update = 0
key_time_limit = 1.0
key_appear_time = 0
level_completed = False

# Кнопки
class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

# Создание кнопок
menu_buttons = [
    Button(WIDTH//2-150, 200+i*120, 300, 80, level["name"])
    for i, level in enumerate(levels)
]
start_button = Button(WIDTH//2-100, 400, 200, 60, "СТАРТ")
back_button = Button(WIDTH//2-100, 400, 200, 60, "МЕНЮ")

def update_frame(success):
    """Обновление кадра: при успехе +1, при промахе -1 (в пределах 1-3)"""
    global current_frame, level_completed, game_state
    
    if success and current_frame != 9:
        current_frame += 1
        # Проверяем, достигли ли мы 9 кадра (победа)
        if current_frame == 9:
            level_completed = True
            game_state = RESULT
    elif not success and current_frame != 1:
        current_frame -= 1
    
    print(f"Кадр изменён на: {current_frame}")  # Отладочный вывод

def draw_menu():
    screen.blit(blue_background, (0, 0))
    title = font_large.render("АРМРЕСТЛИНГ", True, YELLOW)
    screen.blit(title, (WIDTH//2-title.get_width()//2, 100))
    for button in menu_buttons:
        button.draw(screen)

def draw_level_preview():
    screen.blit(animation_frames[5], (0, 0))  # Всегда показываем 2й кадр в превью
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    level = levels[selected_level]
    name = font_large.render(level["name"], True, YELLOW)
    screen.blit(name, (WIDTH//2-name.get_width()//2, 100))

    details = [
        f"Время на клавишу: {level['key_time']} сек",
        "Нажимайте появляющиеся клавиши",
        "Победа: достигните 9 кадра анимации",
        f"Допустимо промахов: {level['miss_limit']}"
    ]
    for i, detail in enumerate(details):
        text = font_small.render(detail, True, WHITE)
        screen.blit(text, (WIDTH//2-text.get_width()//2, 200+i*30))

    start_button.draw(screen)

def draw_countdown():
    screen.blit(animation_frames[5], (0, 0))  
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    if countdown > 0:
        count_text = font_large.render("READY", True, RED)
    else:
        count_text = font_large.render("GO!", True, RED)
    screen.blit(count_text, (WIDTH//2-count_text.get_width()//2, HEIGHT//2-count_text.get_height()//2))

def draw_game():
    """Отрисовка с текущим кадром анимации"""
    screen.blit(animation_frames[current_frame], (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    if current_key:
        time_passed = time.time() - key_appear_time
        progress = min(1.0, time_passed/key_time_limit)
        color = GREEN if current_key.get("pressed", False) else RED if progress >= 1.0 else WHITE
        
        key_text = font_large.render(current_key["key"], True, color)
        screen.blit(key_text, (WIDTH//2-key_text.get_width()//2, HEIGHT//2-50))
        
        pygame.draw.rect(screen, BLACK, (WIDTH//2-100, HEIGHT//2+20, 200, 20), 2)
        pygame.draw.rect(screen, color, (WIDTH//2-98, HEIGHT//2+22, 196*(1-progress), 16))

def draw_result():
    screen.blit(animation_frames[current_frame], (0, 0))
    result_text = font_large.render("ПОБЕДА!" if level_completed else "ПОРАЖЕНИЕ", 
                                  True, GREEN if level_completed else RED)
    screen.blit(result_text, (WIDTH//2-result_text.get_width()//2, 100))

    stats = [
        f"Счет: {score}", 
        f"Промахи: {miss_count}",
        f"Достигнутый кадр: {current_frame}/9",
        "Нажмите МЕНЮ чтобы продолжить"
    ]
    for i, stat in enumerate(stats):
        text = font_medium.render(stat, True, WHITE)
        screen.blit(text, (WIDTH//2-text.get_width()//2, 200+i*50))

    back_button.draw(screen)

def start_level():
    global game_state, countdown, last_countdown_update, current_key
    global score, miss_count, key_time_limit, level_miss_limit, level_completed
    global current_frame

    game_state = COUNTDOWN
    countdown = 3
    last_countdown_update = time.time()
    current_key = None
    score = 0
    miss_count = 0
    key_time_limit = levels[selected_level]["key_time"]
    level_completed = False
    current_frame = 5  # Всегда начинаем с кадра 5 (среднего)

def generate_new_key():
    global current_key, key_appear_time
    current_key = {
        "key": random.choice([chr(i) for i in range(65, 91)] + [str(i) for i in range(10)]),
        "appear_time": time.time(),
        "pressed": False
    }
    key_appear_time = time.time()

def update_countdown():
    global countdown, last_countdown_update, game_state
    if time.time() - last_countdown_update >= 1.0:
        countdown -= 1
        last_countdown_update = time.time()
        if countdown < 0:
            game_state = GAME
            generate_new_key()

def update_game():
    global game_state, score, miss_count, current_key, level_completed
    
    if current_key and not current_key["pressed"]:
        if time.time() - current_key["appear_time"] > key_time_limit:
            score -=1  
            print(score)
            update_frame(False)  # Промах - уменьшаем кадр
            current_key = None
            
            if score <= -4:
                level_completed = False
                game_state = RESULT
                return
                
            pygame.time.set_timer(pygame.USEREVENT, 500)

def handle_events():
    global game_state, selected_level, current_key, score
    
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == MENU:
                for i, button in enumerate(menu_buttons):
                    if button.rect.collidepoint(mouse_pos):
                        selected_level = i
                        game_state = LEVEL_PREVIEW
            elif game_state == LEVEL_PREVIEW and start_button.rect.collidepoint(mouse_pos):
                start_level()
            elif game_state == RESULT and back_button.rect.collidepoint(mouse_pos):
                game_state = MENU
                
        elif event.type == pygame.KEYDOWN and game_state == GAME:
            if current_key and not current_key["pressed"] and event.unicode.upper() == current_key["key"]:
                current_key["pressed"] = True
                score += 1
                update_frame(True)  # Успех - увеличиваем кадр
                pygame.time.set_timer(pygame.USEREVENT, 500)
                
        elif event.type == pygame.USEREVENT and game_state == GAME:
            pygame.time.set_timer(pygame.USEREVENT, 0)
            generate_new_key()

# Главный цикл
clock = pygame.time.Clock()
while True:
    handle_events()
    
    if game_state == COUNTDOWN:
        update_countdown()
    elif game_state == GAME:
        update_game()
    
    if game_state == MENU:
        draw_menu()
    elif game_state == LEVEL_PREVIEW:
        draw_level_preview()
    elif game_state == COUNTDOWN:
        draw_countdown()
    elif game_state == GAME:
        draw_game()
    elif game_state == RESULT:
        draw_result()
    
    pygame.display.flip()
    clock.tick(60)