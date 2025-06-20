import pygame
import sys
import random
import time
import os
import math
from settings import *
from Button import Button

class Game:
    def __init__(self):
        self.levels = [
            {"name": "Новичок", "required_speed": 3, 
             "stamina_drain": 0.3, "stamina_recover": 0.3, "qte_chance": 0.003},
            {"name": "Средний", "required_speed": 5, 
             "stamina_drain": 0.4, "stamina_recover": 0.25, "qte_chance": 0.005},
            {"name": "Профи", "required_speed": 7,
             "stamina_drain": 0.5, "stamina_recover": 0.2, "qte_chance": 0.007}
        ]
        
        self.state = "MENU"
        self.selected_level = 0
        self.reset_game_state()
        
        # Загрузка ресурсов
        self.animation_frames = None
        self.current_frame = None
        self.blue_background = self.create_blue_background()
        self.sound_effect = None
        
        # Создание кнопок
        self.buttons = {
            "menu": [Button(WIDTH//2-150, 300+i*120, 300, 80, level["name"]) for i, level in enumerate(self.levels)],
            "start": Button(WIDTH//2-100, HEIGHT-200, 200, 60, "СТАРТ"),
            "back": Button(WIDTH//2-100, HEIGHT-200, 200, 60, "МЕНЮ")
        }
    
    def reset_game_state(self):
        self.base_path_to = f"files_of_game/{self.selected_level + 1}/frames/"
        self.current_frame = self.take_length_picture(self.base_path_to, ".jpg")//2 if self.take_length_picture(self.base_path_to, ".jpg") else None
        self.animation_frames = self.load_animation_frames()
        self.high_limit_frames = self.take_length_picture(self.base_path_to, ".jpg")
        self.low_limit_frames = 1
        self.press_count = 0
        self.start_time = 0
        self.countdown = 3
        self.last_countdown_update = 0
        self.level_completed = False
        self.last_press_time = 0
        self.current_speed = 0
        self.last_speed_update = 0
        self.presses_in_period = 0
        self.stamina = 100
        self.last_stamina_update = 0
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.screen_shake_timer = 0
        self.qte_active = False
        self.qte_key = None
        self.qte_timer = 0
        self.qte_duration = 2  
        self.sound_effect = self.load_sound_effect()
        self.music = self.load_music()
        self.sound_game_effect = self.load_sound_effect_in_game()
        self.temp_playing = 0

    def load_sound_effect(self):
        if(self.state != "LEVEL_PREVIEW"): return None
        effect_ = {}
        for i in range(2):
            sound_effect = pygame.mixer.Sound(f"project/files_of_game/{self.selected_level + 1}/music/sound_effect/{i + 1}.wav")
            sound_effect.set_volume(0.7)
            effect_[i + 1] = sound_effect
        return effect_
    
    def load_sound_effect_in_game(self):
        if(self.state != "LEVEL_PREVIEW"): return None

        count_of_effect = self.take_length_picture(f"files_of_game/{self.selected_level + 1}/music/sound_effect_in_game/", ".wav")
        effect_ = {}
        for i in range(count_of_effect):
            sound_effect = pygame.mixer.Sound(f"project/files_of_game/{self.selected_level + 1}/music/sound_effect_in_game/{i + 1}.wav")
            sound_effect.set_volume(0.7)
            effect_[i + 1] = sound_effect
        return effect_
    
    def load_music(self):
        if(self.state != "LEVEL_PREVIEW"): return None
        music = pygame.mixer.Sound(f"project/files_of_game/{self.selected_level + 1}/music/sound.mp3")
        music.set_volume(0.1)
        return music

    def take_length_picture(self, path:str, sp:str):
        if(self.state != "LEVEL_PREVIEW"): return None

        base_path = os.path.dirname(os.path.abspath(__file__))
        frames_dir = os.path.join(base_path, path)

        try:
            frame_files = sorted(
            [f for f in os.listdir(frames_dir) if f.endswith(sp)],
            key=lambda x: int(x.split('.')[0])
            )   
        except:
            frame_files = []

        return len(frame_files)

    def load_animation_frames(self):
        if(self.state != "LEVEL_PREVIEW"): return None

        frames = {}
        base_path = os.path.dirname(os.path.abspath(__file__))
        lenght_ = self.take_length_picture(f"files_of_game/{self.selected_level + 1}/frames/", ".jpg")
        
        for i in range(lenght_, 0, -1):
            if (self.selected_level == 1): frame_idx = i
            else: frame_idx = (lenght_ + 1) - i
            try:
                image_path = os.path.join(base_path, f"files_of_game/{self.selected_level + 1}/frames/{i}.jpg")
                frames[frame_idx] = pygame.transform.scale(pygame.image.load(image_path), (WIDTH, HEIGHT))
            except:
                frames[frame_idx] = self.create_color_surface()
        
       #  if(self.selected_level == 1): return reversed(frames)

        return frames
    
    def load_one_frame(self):
        image = None
        base_path = os.path.dirname(os.path.abspath(__file__))

        if(self.level_completed):
            image_path = os.path.join(base_path, f"files_of_game/{self.selected_level + 1}/victory_image/1.png")
            image = pygame.transform.scale(pygame.image.load(image_path), (WIDTH, HEIGHT))
        else:
            image_path = os.path.join(base_path, f"files_of_game/{self.selected_level + 1}/lose_image/1.png")
            image = pygame.transform.scale(pygame.image.load(image_path), (WIDTH, HEIGHT))

        return image
    
    def create_color_surface(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        surface.fill(color)
        return surface
    
    def create_blue_background(self):
        background = pygame.Surface((WIDTH, HEIGHT))
        top_color = (20, 50, 100)
        bottom_color = (80, 150, 220)
        
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
        
        return background
    
    def start_level(self):
        self.reset_game_state()
        self.state = "COUNTDOWN"
        self.last_countdown_update = time.time()
    
    def update(self):
        if self.state == "COUNTDOWN":
            self.update_countdown()
        elif self.state == "LEVEL_PREVIEW":
            self.reset_game_state()
        elif self.state == "GAME":
            self.update_gameplay()
        
        # Обновление тряски экрана
        if self.screen_shake_timer < self.screen_shake_duration:
            self.screen_shake_timer += 1/60
    
    def update_countdown(self):
        if time.time() - self.last_countdown_update >= 1.0:
            self.countdown -= 1
            self.last_countdown_update = time.time()
            if self.countdown <= 0:
                self.state = "GAME"
                self.music.play(loops=-1)
                self.start_time = time.time()
    
    def choise_effect(self):
        self.temp_playing = random.choice(list(self.sound_game_effect.keys()))
        self.sound_game_effect[self.temp_playing].play()

    def update_gameplay(self):
        current_time = time.time()
        level = self.levels[self.selected_level]

        # Обновление стамины
        if current_time - self.last_stamina_update >= 0.1:
            if self.presses_in_period > 0:
                self.stamina -= self.levels[self.selected_level]["stamina_drain"] * self.presses_in_period
                self.stamina = max(0, self.stamina)
            else:
                self.stamina += self.levels[self.selected_level]["stamina_recover"]
                self.stamina = min(100, self.stamina)
            self.last_stamina_update = current_time
        
        # Обновление скорости нажатий
        if current_time - self.last_speed_update >= 0.1:
            time_passed = current_time - self.last_speed_update
            self.current_speed = self.presses_in_period / time_passed if time_passed > 0 else 0
            self.presses_in_period = 0
            self.last_speed_update = current_time
            
            # Проверка условий для изменения кадра
            efficiency = 0.5 + (self.stamina / 200)
            
            if (self.current_speed >= level['required_speed']/5 * efficiency * 0.7):
                self.update_frame(True)
            else:
                self.update_frame(False)
        
        # Проверка QTE
        if not self.qte_active and random.random() < level["qte_chance"] and current_time - self.start_time > 5:
            self.start_qte_event()
            if(self.temp_playing != 0):
                 self.sound_game_effect[self.temp_playing].stop()
            self.choise_effect() 
        
        if self.qte_active and current_time - self.qte_timer > self.qte_duration:
            self.qte_active = False
            for _ in range(2):
                self.update_frame(False)
            self.trigger_screen_shake(10, 1)

    def update_music_mov(self):
        self.music.stop()
        if(self.temp_playing != 0):
            self.sound_game_effect[self.temp_playing].stop()
        if(self.level_completed): self.sound_effect[1].play()
        else: self.sound_effect[2].play()

    def update_frame(self, success):
        if success and self.current_frame < self.high_limit_frames:
            self.current_frame += 1
            if self.current_frame == self.high_limit_frames:
                self.level_completed = True
                self.state = "RESULT"
                self.update_music_mov()
                self.trigger_screen_shake(20, 2)
        elif not success and self.current_frame > self.low_limit_frames:
            self.current_frame -= 1
            if self.current_frame == self.low_limit_frames  :
                self.level_completed = False
                self.state = "RESULT"
                self.update_music_mov()
                self.trigger_screen_shake(15, 1.2)

        print(f"Сейчас {self.current_frame} кадр")
    
    def start_qte_event(self):
        self.qte_active = True
        self.qte_key = random.choice([pygame.K_f, pygame.K_j])
        self.qte_timer = time.time()
        self.trigger_screen_shake(10, 1)
    
    def trigger_screen_shake(self, intensity, duration):
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration
        self.screen_shake_timer = 0
    
    def get_screen_shake_offset(self):
        if self.screen_shake_timer < self.screen_shake_duration:
            progress = self.screen_shake_timer / self.screen_shake_duration
            current_intensity = self.screen_shake_intensity * (1 - progress)
            offset_x = math.sin(self.screen_shake_timer * 50) * current_intensity
            offset_y = math.cos(self.screen_shake_timer * 30) * current_intensity
            return (int(offset_x), int(offset_y))
        return (0, 0)
    
    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "LEVEL_PREVIEW":
            self.draw_level_preview()
        elif self.state == "COUNTDOWN":
            self.draw_countdown()
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "RESULT":
            self.draw_result()
        
        pygame.display.flip()
    
    def draw_menu(self):
        screen.blit(self.blue_background, (0, 0))
        title = font_large.render("IRON HANDS", True, YELLOW)
        screen.blit(title, (WIDTH//2-title.get_width()//2, 100))
        for button in self.buttons["menu"]:
            button.draw(screen)
    
    def draw_level_preview(self):
        screen.blit(self.animation_frames[self.current_frame], (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        level = self.levels[self.selected_level]
        name = font_large.render(level["name"], True, YELLOW)
        screen.blit(name, (WIDTH//2-name.get_width()//2, 100))

        self.buttons["start"].draw(screen)
    
    def draw_countdown(self):
        screen.blit(self.animation_frames[self.current_frame], (0, 0))  
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        if self.countdown > 1:
            count_text = font_large.render("READY", True, RED)
        else:
            count_text = font_large.render("GO!", True, RED)
        screen.blit(count_text, (WIDTH//2-count_text.get_width()//2, HEIGHT//2-count_text.get_height()//2))
    
    
    def draw_stamina_bar(self):
        bar_width = 200
        bar_height = 20
        x = WIDTH - bar_width - 20
        y = 20
        
        pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height))
        fill_width = (self.stamina / 100) * bar_width
        color = GREEN if self.stamina > 50 else ORANGE if self.stamina > 25 else RED
        pygame.draw.rect(screen, color, (x, y, fill_width, bar_height))
        pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
        
        text = font_small.render(f"Выносливость: {int(self.stamina)}%", True, WHITE)
        screen.blit(text, (x, y + bar_height + 5))
    
    
    def draw_game(self):
        offset = self.get_screen_shake_offset()
        screen.blit(self.animation_frames[self.current_frame], offset)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Инструкция
        instr_text = font_small.render("Быстро нажимайте ПРОБЕЛ!", True, YELLOW)
        screen.blit(instr_text, (WIDTH//2-instr_text.get_width()//2, HEIGHT-100))

        # Шкала стамины
        self.draw_stamina_bar()
        
        # QTE
        if self.qte_active:
            self.draw_qte()

    def draw_qte(self):
        panel = pygame.Surface((400, 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 0))
        screen.blit(panel, (WIDTH//2-200, HEIGHT//2-75))
        
        text = font_large.render(f"Нажмите {'F' if self.qte_key == pygame.K_f else 'J'}", True, WHITE)
        screen.blit(text, (WIDTH//2-text.get_width()//2, HEIGHT//2-25))
        
        time_left = max(0, 2 - (time.time() - self.qte_timer))
        timer_width = 300 * (time_left / 2)
        timer_color = (
            int(255 * (1 - time_left/2)),
            int(255 * (time_left/2)),
            0
        )
        pygame.draw.rect(screen, timer_color, (WIDTH//2-150, HEIGHT//2+45, timer_width, 15))
    
    def draw_result(self):
        frame  = self.load_one_frame()
        screen.blit(frame, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        text = font_large.render("ПОБЕДА!" if self.level_completed else "ПОРАЖЕНИЕ", 
                               True, GREEN if self.level_completed else RED)
        screen.blit(text, (WIDTH//2-text.get_width()//2, 100))

        self.buttons["back"].draw(screen)