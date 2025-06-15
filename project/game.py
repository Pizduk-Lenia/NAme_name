import pygame
import sys
import random
import time
import os
import math  # Для тряски экрана

# Инициализация Pygame
pygame.init()

# Настройки экрана (полноэкранный режим)
WIDTH, HEIGHT = 1280, 720
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
ORANGE = (255, 165, 0)

# Шрифты
font_large = pygame.font.SysFont('Arial', 72, bold=True)
font_medium = pygame.font.SysFont('Arial', 48)
font_small = pygame.font.SysFont('Arial', 24)

# Создание синего фона
def create_blue_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    
    # Цвета для градиента (можно настроить)
    top_color = (20, 50, 100)      # Темный синий (верх)
    bottom_color = (80, 150, 220)  # Светлый синий (низ)
    
    for y in range(HEIGHT):
        # Интерполяция цвета
        ratio = y / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        
        # Ограничение значений
        color = (
            max(0, min(255, r)),
            max(0, min(255, g)),
            max(0, min(255, b))
        )
        
        pygame.draw.line(background, color, (0, y), (WIDTH, y))
    
    return background

blue_background = create_blue_background()

# Загрузка кадров анимации (1-65)
def load_animation_frames():
    frames = {}
    base_path = os.path.dirname(os.path.abspath(__file__))
    j = 1
    for i in range(34, 0, -1):  
        try:
            image_path = os.path.join(base_path, f"lose/{i}.jpg")
            image = pygame.image.load(image_path)
            frames[j] = pygame.transform.scale(image, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Ошибка загрузки кадра {j}: {e}")
            # Создаем простой цветной фон для отсутствующих кадров
            frames[j] = pygame.Surface((WIDTH, HEIGHT))
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            frames[j].fill(color)
        j += 1
    
    try:
        image_path = os.path.join(base_path, f"static/{1}.jpg")
        image = pygame.image.load(image_path)
        frames[35] = pygame.transform.scale(image, (WIDTH, HEIGHT))
    except Exception as e:
            print(f"Ошибка загрузки кадра {1}: {e}")
            # Создаем простой цветной фон для отсутствующих кадров
            frames[35] = pygame.Surface((WIDTH, HEIGHT))
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            frames[35].fill(color)

    for i in range(1, 35):  
        try:
            image_path = os.path.join(base_path, f"win/{i}.jpg")
            image = pygame.image.load(image_path)
            frames[i + 35] = pygame.transform.scale(image, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Ошибка загрузки кадра {i}: {e}")
            # Создаем простой цветной фон для отсутствующих кадров
            frames[i + 35] = pygame.Surface((WIDTH, HEIGHT))
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            frames[i + 35].fill(color)
    
    return frames

animation_frames = load_animation_frames()
current_frame = 35  # Центральный кадр (35 из 69)

# Уровни игры
levels = [
    {"name": "Новичок", "required_speed": 3, "required_presses": 15, "stamina_drain": 0.3, "stamina_recover": 0.3, "chance" : 0.003},
    {"name": "Средний", "required_speed": 5, "required_presses": 25, "stamina_drain": 0.4, "stamina_recover": 0.25, "chance" : 0.005},
    {"name": "Профи", "required_speed": 7, "required_presses": 35, "stamina_drain": 0.5, "stamina_recover": 0.2, "chance" : 0.007}
]

# Игровые состояния
MENU = 0
LEVEL_PREVIEW = 1
COUNTDOWN = 2
GAME = 3
RESULT = 4
QTE_EVENT = 5  # Новое состояние для QTE

# Игровые переменные
game_state = MENU
selected_level = 0
score = 0  # Начинаем с центрального кадра (35)
press_count = 0
start_time = 0
countdown = 3
last_countdown_update = 0
level_completed = False
last_press_time = 0
current_speed = 0
total_presses = 0
last_speed_update = 0
presses_in_period = 0
victory_cadr = None
lose_cadr = None

# Новые переменные для механик
stamina = 100  # Шкала выносливости (0-100)
stamina_depletion_rate = levels[0]["stamina_drain"]  # Скорость снижения стамины при нажатиях
stamina_recovery_rate = levels[0]["stamina_recover"]  # Скорость восстановления стамины
last_stamina_update = 0

screen_shake_intensity = 0  # Интенсивность тряски экрана
screen_shake_duration = 0  # Длительность тряски
screen_shake_timer = 0  # Таймер тряски

qte_active = False  # Активно ли QTE-событие
qte_key = None  # Какую клавишу нужно нажать для QTE
qte_timer = 0  # Таймер QTE
qte_duration = 2  # Длительность QTE (секунды)
qte_success = False  # Успешно ли выполнено QTE
qte_fail = False  # Провалено ли QTE

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

def trigger_screen_shake(intensity, duration):
    """Активирует тряску экрана"""
    global screen_shake_intensity, screen_shake_duration, screen_shake_timer
    screen_shake_intensity = intensity
    screen_shake_duration = duration
    screen_shake_timer = 0

def apply_screen_shake():
    """Возвращает смещение для тряски экрана"""
    global screen_shake_timer
    if screen_shake_timer < screen_shake_duration:
        # Плавное затухание тряски
        progress = screen_shake_timer / screen_shake_duration
        current_intensity = screen_shake_intensity * (1 - progress)
        
        # Синусоидальное движение для более натуральной тряски
        offset_x = math.sin(screen_shake_timer * 50) * current_intensity
        offset_y = math.cos(screen_shake_timer * 30) * current_intensity
        
        screen_shake_timer += 1/60
        return (int(offset_x), int(offset_y))
    return (0, 0)

def start_qte_event():
    """Начинает QTE-событие"""
    global qte_active, qte_key, qte_timer, qte_success, qte_fail
    qte_active = True
    qte_key = random.choice([pygame.K_f, pygame.K_j])
    qte_timer = time.time()
    qte_success = False
    qte_fail = False
    trigger_screen_shake(20, 2)  # Увеличиваем тряску для QTE

def update_frame(success):
    """Обновление кадра: при успехе +1, при промахе -1 (в пределах 1-69)"""
    global current_frame, level_completed, game_state, score
    
    if success and current_frame < 69:
        current_frame += 1
        score += 1
        # Проверяем, достигли ли мы 69 кадра (победа)
        if current_frame == 69:
            level_completed = True
            game_state = RESULT
            trigger_screen_shake(20, 2)  # Сильная тряска при победе
    elif not success and current_frame > 1:
        current_frame -= 1
        score -= 1
        # Проверяем, достигли ли мы 1 кадра (поражение)
        if current_frame == 1:
            level_completed = False
            game_state = RESULT
            trigger_screen_shake(25, 2.5)  # Очень сильная тряска при поражении
    
    print(f"Кадр изменён на: {current_frame}, Счет: {score}")  # Отладочный вывод

def draw_menu():
    screen.blit(blue_background, (0, 0))
    title = font_large.render("АРМРЕСТЛИНГ", True, YELLOW)
    screen.blit(title, (WIDTH//2-title.get_width()//2, 100))
    for button in menu_buttons:
        button.draw(screen)

def draw_level_preview():
    screen.blit(animation_frames[35], (0, 0))  # Показываем центральный кадр в превью
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    level = levels[selected_level]
    name = font_large.render(level["name"], True, YELLOW)
    screen.blit(name, (WIDTH//2-name.get_width()//2, 100))

    start_button.draw(screen)

def draw_countdown():
    screen.blit(animation_frames[35], (0, 0))  
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
    # Создаем временную поверхность для тряски
    temp_surface = pygame.Surface((WIDTH, HEIGHT))
    shake_offset = apply_screen_shake()
    
    # Рисуем основной кадр со смещением
    screen.blit(animation_frames[current_frame], shake_offset)
    
    # Затемнение (но не полное - убираем alpha=150)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    # Инструкция
    instr_text = font_small.render("Быстро нажимайте ПРОБЕЛ!", True, YELLOW)
    screen.blit(instr_text, (WIDTH//2-instr_text.get_width()//2, HEIGHT-100))

    # Отрисовка шкалы стамины
    stamina_bar_width = 200
    stamina_bar_height = 20
    stamina_bar_x = WIDTH - stamina_bar_width - 20
    stamina_bar_y = 20
    
    # Фон шкалы
    pygame.draw.rect(screen, GRAY, (stamina_bar_x, stamina_bar_y, stamina_bar_width, stamina_bar_height))
    # Заполнение шкалы
    stamina_fill = (stamina / 100) * stamina_bar_width
    stamina_color = GREEN if stamina > 50 else ORANGE if stamina > 25 else RED
    pygame.draw.rect(screen, stamina_color, (stamina_bar_x, stamina_bar_y, stamina_fill, stamina_bar_height))
    # Обводка
    pygame.draw.rect(screen, BLACK, (stamina_bar_x, stamina_bar_y, stamina_bar_width, stamina_bar_height), 2)
    
    # Текст стамины
    stamina_text = font_small.render(f"Выносливость: {int(stamina)}%", True, WHITE)
    screen.blit(stamina_text, (stamina_bar_x, stamina_bar_y + stamina_bar_height + 5))

    # Отрисовка QTE, если оно активно
    if qte_active:
         # Полупрозрачная панель QTE
        qte_panel = pygame.Surface((400, 150), pygame.SRCALPHA)
        qte_panel.fill((0, 0, 0, 0))
        screen.blit(qte_panel, (WIDTH//2-200, HEIGHT//2-75))
        
        qte_text = font_large.render("Нажмите " + ("F" if qte_key == pygame.K_f else "J"), True, WHITE)
        screen.blit(qte_text, (WIDTH//2-qte_text.get_width()//2, HEIGHT//2-25))
        
        # Таймер QTE с анимацией
        time_left = max(0, qte_duration - (time.time() - qte_timer))
        timer_width = 300 * (time_left / qte_duration)
        
        # Анимированный индикатор - меняет цвет
        timer_color = (
            int(255 * (1 - time_left/qte_duration)),
            int(255 * (time_left/qte_duration)),
            0
        )
        pygame.draw.rect(screen, timer_color, (WIDTH//2-150, HEIGHT//2+30 + 15, timer_width, 15))
        
def draw_result():
    if level_completed:
        screen.blit(animation_frames[69], (0, 0))  # Показываем последний кадр победы
    else:
        screen.blit(animation_frames[1], (0, 0))  # Показываем первый кадр поражения
        
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    result_text = font_large.render("ПОБЕДА!" if level_completed else "ПОРАЖЕНИЕ", 
                                  True, GREEN if level_completed else RED)
    screen.blit(result_text, (WIDTH//2-result_text.get_width()//2, 100))

    back_button.draw(screen)

def start_level():
    global game_state, countdown, last_countdown_update, selected_level, lose_cadr
    global press_count, start_time, level_completed, current_frame, score
    global last_press_time, current_speed, total_presses, presses_in_period, last_speed_update
    global stamina, last_stamina_update, qte_active, stamina_depletion_rate, stamina_recovery_rate

    game_state = COUNTDOWN
    countdown = 3
    last_countdown_update = time.time()
    press_count = 0
    start_time = 0
    level_completed = False
    current_frame = 35  # Начинаем с центрального кадра
    score = 0  # Счет соответствует кадру
    last_press_time = 0
    current_speed = 0
    total_presses = 0
    presses_in_period = 0
    last_speed_update = time.time()
    stamina = 100  # Восстанавливаем стамину
    last_stamina_update = time.time()
    qte_active = False  # Сбрасываем QTE
    
    # Устанавливаем параметры стамины для выбранного уровня
    stamina_depletion_rate = levels[selected_level]["stamina_drain"]
    stamina_recovery_rate = levels[selected_level]["stamina_recover"]

    base_path = os.path.dirname(os.path.abspath(__file__))
    lose = os.path.join(base_path, f"losing_folder/{selected_level + 1}.jpg")
    lose_cadr = pygame.image.load(lose)

def update_countdown():
    global countdown, last_countdown_update, game_state, start_time
    if time.time() - last_countdown_update >= 1.0:
        countdown -= 1
        last_countdown_update = time.time()
        if countdown <= 0:
            game_state = GAME
            start_time = time.time()

def update_game():
    global current_speed, press_count, last_press_time, last_countdown_update
    global total_presses, presses_in_period, last_speed_update
    global stamina, last_stamina_update
    global qte_active, qte_timer, qte_success, qte_fail, screen_shake_timer, screen_shake_duration
    
    current_time = time.time()
    
    # Обновление таймера тряски экрана
    if screen_shake_timer < screen_shake_duration:
        screen_shake_timer += 1/60  # Примерно 1 кадр
    
    # Обновление стамины
    if current_time - last_stamina_update >= 0.1:  # Обновляем стамину каждые 0.1 секунды
        if presses_in_period > 0:
            stamina -= stamina_depletion_rate * presses_in_period
            stamina = max(0, stamina)
        else:
            stamina += stamina_recovery_rate
            stamina = min(100, stamina)
        last_stamina_update = current_time
    
    # Обновление скорости нажатий
    if current_time - last_speed_update >= 0.1:  # Увеличил интервал проверки скорости до 0.5 сек
        time_passed = current_time - last_speed_update
        current_speed = presses_in_period / time_passed if time_passed > 0 else 0
        presses_in_period = 0
        last_speed_update = current_time
        
        # Проверяем, соответствует ли скорость требованиям уровня (с учетом стамины)
        required_speed = levels[selected_level]['required_speed']/5
        required_presses = levels[selected_level]['required_presses']/5
        
        # Эффективность зависит от стамины (чем меньше стамина, тем сложнее)
        efficiency = 0.5 + (stamina / 200)  # От 0.5 до 1.0
        
        # Условия успеха сделаны более мягкими
        if current_speed >= required_speed * efficiency * 0.7 and total_presses >= required_presses * 0.7:
            update_frame(True)  # Успех - увеличиваем кадр
        else:
            update_frame(False)  # Недостаточная скорость - уменьшаем кадр
    
    # Проверка на активацию QTE (случайное событие)
    if not qte_active and random.random() < levels[selected_level]["chance"] and current_time - start_time > 5:  # 0.3% шанс каждый кадр после 5 секунд игры
        start_qte_event()
    
    # Обновление QTE
    if qte_active:
        if current_time - qte_timer > qte_duration:
            qte_active = False
            qte_fail = True
            # Наказание за провал QTE
            for _ in range(2):  # Проигрываем 2 кадра (было 3)
                update_frame(False)
            trigger_screen_shake(22, 2)  # Уменьшил тряску при провале

def handle_events():
    global game_state, selected_level, press_count, last_press_time, total_presses, presses_in_period
    global qte_active, qte_success, qte_fail, stamina
    
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Выход по ESC
                pygame.quit()
                sys.exit()
                
            if game_state == GAME:
                if qte_active:
                    # Обработка QTE
                    if event.key == qte_key:
                        qte_active = False
                        qte_success = True
                        # Награда за успешное QTE
                        for _ in range(3):  # Выигрываем 3 кадра (было 5)
                            update_frame(True)
                        stamina = min(100, stamina + 15)  # Восстанавливаем часть стамины
                        trigger_screen_shake(10, 1.2)  # Уменьшил тряску при успехе
                    elif event.key in [pygame.K_f, pygame.K_j]:
                        # Нажата не та клавиша
                        qte_fail = True
                
                if event.key == pygame.K_SPACE and not qte_active:
                    # Основной геймплей
                    if stamina > 0:  # Можно нажимать только если есть стамина
                        press_count += 1
                        total_presses += 1
                        presses_in_period += 1
                        last_press_time = time.time()
                        stamina -= stamina_depletion_rate  # Тратим стамину
                        stamina = max(0, stamina)
                        
                        # Небольшая тряска при каждом нажатии
                        trigger_screen_shake(7, 1.3)  # Уменьшил тряску при нажатиях
            
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