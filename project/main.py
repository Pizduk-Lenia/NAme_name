import pygame
import sys
from Game import Game
import time

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        # Обработка событий
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                if game.state == "GAME":
                    if game.qte_active:
                        if event.key == game.qte_key:
                            game.qte_active = False
                            for _ in range(3):
                                game.update_frame(True)
                            game.stamina = min(100, game.stamina + 15)
                            game.trigger_screen_shake(10, 1.2)
                        elif event.key in [pygame.K_f, pygame.K_j]:
                            game.qte_fail = True
                    
                    if event.key == pygame.K_SPACE and not game.qte_active and game.stamina > 0:
                        game.press_count += 1
                        game.total_presses += 1
                        game.presses_in_period += 1
                        game.last_press_time = time.time()
                        game.stamina -= game.levels[game.selected_level]["stamina_drain"]
                        game.stamina = max(0, game.stamina)
                        game.trigger_screen_shake(5, 0.5)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state == "MENU":
                    for i, button in enumerate(game.buttons["menu"]):
                        if button.rect.collidepoint(mouse_pos):
                            game.selected_level = i
                            game.state = "LEVEL_PREVIEW"
                elif game.state == "LEVEL_PREVIEW" and game.buttons["start"].rect.collidepoint(mouse_pos):
                    game.start_level()
                elif game.state == "RESULT" and game.buttons["back"].rect.collidepoint(mouse_pos):
                    game.state = "MENU"
        
        # Обновление состояния игры
        game.update()
        
        # Отрисовка
        game.draw()
        
        # Обновление hover состояния кнопок
        if game.state == "MENU":
            for button in game.buttons["menu"]:
                button.check_hover(mouse_pos)
        elif game.state in ["LEVEL_PREVIEW", "RESULT"]:
            game.buttons["start" if game.state == "LEVEL_PREVIEW" else "back"].check_hover(mouse_pos)
        
        clock.tick(60)

if __name__ == "__main__":
    main()