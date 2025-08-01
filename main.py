import pygame
import sys
import time
import random
import math
import heapq
import os
from pygame.locals import *
from collections import defaultdict
from languages import TRANSLATIONS

# Initialize Pygame
pygame.init()

# Constants
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
CELL_SIZE = 48
PLAYER_SIZE = int(CELL_SIZE * 0.8)
BOSS_SIZE = int(CELL_SIZE * 0.8)
LETTER_SIZE = 32
VISION_RADIUS = 2  
FOG_ALPHA = 100

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
# Difficulty settings
DIFFICULTY_SETTINGS = {
    'easy': {
        'speeds': {
            'normal': 1,    # Langsamer
            'fast': 1.5,    # Langsamer
            'faster': 2,    # Langsamer
            'fastest': 2.5  # Langsamer
        },
        'time_limit': 600,  # 10 Minuten
        'letters': "DETMOLD",
        'num_bosses': 3  # Immer 3 Bosse: Tom, Jannik, Louis
    },
    'medium': {
        'speeds': {
            'normal': 1.5,
            'fast': 2,
            'faster': 2.5,
            'fastest': 3
        },
        'time_limit': 420,  # 7 Minuten
        'letters': "DETMOLD",
        'num_bosses': 3  # Immer 3 Bosse: Tom, Jannik, Louis
    },
    'hard': {
        'speeds': {
            'normal': 2,
            'fast': 2.5,
            'faster': 3,
            'fastest': 3.5
        },
        'time_limit': 300,  # 5 Minuten
        'letters': "DETMOLD",
        'num_bosses': 3  # Immer 3 Bosse: Tom, Jannik, Louis
    }
}

# Maze layout: 0 = path, 1 = wall
MAZE_LAYOUT = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Berechne die Spielfeldgröße
GAME_WIDTH = len(MAZE_LAYOUT[0]) * CELL_SIZE
GAME_HEIGHT = len(MAZE_LAYOUT) * CELL_SIZE

# Zentriere das Spiel auf dem Display
GAME_OFFSET_X = (DISPLAY_WIDTH - GAME_WIDTH) // 2
GAME_OFFSET_Y = (DISPLAY_HEIGHT - GAME_HEIGHT) // 2

class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        # Make hitbox even smaller (40% of visual size)
        hitbox_size = int(PLAYER_SIZE * 0.4)
        hitbox_offset = (PLAYER_SIZE - hitbox_size) // 2
        self.rect = pygame.Rect(x + hitbox_offset, y + hitbox_offset, hitbox_size, hitbox_size)
        self.visual_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = 8
        self.interaction_cooldown = 0
        self.image = image
        self.last_move_time = time.time()
        self.move_delay = 0.01  # Add slight delay between movements

    def handle_input(self, walls):
        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            return

        dx = 0
        dy = 0

        # Tastatureingaben
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] or keys[K_a]:
            dx = -self.speed
        if keys[K_RIGHT] or keys[K_d]:
            dx = self.speed
        if keys[K_UP] or keys[K_w]:
            dy = -self.speed
        if keys[K_DOWN] or keys[K_s]:
            dy = self.speed

        # Controller-Eingaben
        for joystick in [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]:
            # Linker Analogstick
            x_axis = joystick.get_axis(0)  # X-Achse
            y_axis = joystick.get_axis(1)  # Y-Achse
            
            # Deadzone für Analogstick
            deadzone = 0.2
            if abs(x_axis) > deadzone:
                dx = self.speed * x_axis
            if abs(y_axis) > deadzone:
                dy = self.speed * y_axis
                
            # D-Pad
            hat = joystick.get_hat(0)
            if hat[0] == -1:  # Links
                dx = -self.speed
            elif hat[0] == 1:  # Rechts
                dx = self.speed
            if hat[1] == 1:   # Oben
                dy = -self.speed
            elif hat[1] == -1: # Unten
                dy = self.speed
            
            # X-Taste für Interaktion
            if joystick.get_button(0):  # X-Button (PS4)
                self.interaction_cooldown = 30  # Setzt den Cooldown
        
        if dx != 0 or dy != 0:
            self.move(dx, dy, walls)
            self.last_move_time = current_time

    def move(self, dx, dy, walls):
        # Move at constant speed
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Update both visual and hitbox rectangles
        hitbox_size = int(PLAYER_SIZE * 0.4)
        hitbox_offset = (PLAYER_SIZE - hitbox_size) // 2
        temp_rect = pygame.Rect(new_x + hitbox_offset, new_y + hitbox_offset, hitbox_size, hitbox_size)
        
        can_move = True
        for wall in walls:
            if temp_rect.colliderect(wall['rect']):
                can_move = False
                break
        
        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect.x = new_x + hitbox_offset
            self.rect.y = new_y + hitbox_offset
            self.visual_rect.x = new_x
            self.visual_rect.y = new_y

    def draw(self, screen):
        screen.blit(self.image, (self.visual_rect.x + GAME_OFFSET_X, self.visual_rect.y + GAME_OFFSET_Y))
        # Debug: Draw hitbox in red
        pygame.draw.rect(screen, RED, (self.rect.x + GAME_OFFSET_X, self.rect.y + GAME_OFFSET_Y, self.rect.width, self.rect.height), 1)

class Boss:
    def __init__(self, x, y, name, speed, image, spawn_time, difficulty='medium'):
        self.x = x
        self.y = y
        self.hitbox_size = int(BOSS_SIZE * 0.6)  # Kleinere Hitbox
        self.hitbox_offset = (BOSS_SIZE - self.hitbox_size) // 2
        self.rect = pygame.Rect(x + self.hitbox_offset, y + self.hitbox_offset, self.hitbox_size, self.hitbox_size)
        self.visual_rect = pygame.Rect(x, y, BOSS_SIZE, BOSS_SIZE)
        self.name = name
        self.base_speed = speed
        self.speed = speed
        self.image = image
        self.spawn_time = spawn_time
        self.active = False
        self.name_font = pygame.font.Font(None, 20)
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30  # Update alle 0.5 Sekunden (30 Frames)
        self.last_player_pos = None
        self.difficulty = difficulty
        # Zufälliger Offset für das Ziel (1-2 Felder)
        self.target_offset = (
            random.randint(-2 * CELL_SIZE, 2 * CELL_SIZE),
            random.randint(-2 * CELL_SIZE, 2 * CELL_SIZE)
        )
        
    def update(self, player, walls):
        if not self.active and time.time() >= self.spawn_time:
            self.active = True
        
        if not self.active:
            return
            
        # Position und Hitbox aktualisieren
        self.rect.x = self.x + self.hitbox_offset
        self.rect.y = self.y + self.hitbox_offset
        self.visual_rect.x = self.x
        self.visual_rect.y = self.y
        
        # Pfad-Update Timer
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval:
            self.path_update_timer = 0
            # Ziel mit Offset berechnen
            target_x = player.rect.centerx + self.target_offset[0]
            target_y = player.rect.centery + self.target_offset[1]
            # Stelle sicher, dass das Ziel im Spielfeld liegt
            target_x = max(CELL_SIZE, min(target_x, (len(MAZE_LAYOUT[0])-2) * CELL_SIZE))
            target_y = max(CELL_SIZE, min(target_y, (len(MAZE_LAYOUT)-2) * CELL_SIZE))
            self.last_player_pos = (target_x, target_y)
            # Neuen Pfad berechnen
            self.path = self.find_path_to_player(player, walls)
            # Geschwindigkeit leicht variieren
            self.speed = self.base_speed * random.uniform(0.9, 1.1)
        
        # Bewegung entlang des Pfades
        if self.path:
            next_x, next_y = self.path[0]
            dx = next_x - self.rect.centerx
            dy = next_y - self.rect.centery
            
            # Bewegungsvektor normalisieren
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                # Neue Position testen
                new_x = self.x + dx
                new_y = self.y + dy
                
                # Kollisionstest
                test_rect = pygame.Rect(new_x + self.hitbox_offset, new_y + self.hitbox_offset, 
                                     self.hitbox_size, self.hitbox_size)
                
                can_move = True
                for wall in walls:
                    if test_rect.colliderect(wall['rect']):
                        can_move = False
                        break
                
                if can_move:
                    self.x = new_x
                    self.y = new_y
                    
                # Wegpunkt erreicht?
                if distance < self.speed * 2:
                    self.path.pop(0)
    
    def find_path_to_player(self, player, walls):
        if not self.last_player_pos:
            return []
            
        # Start- und Zielpositionen
        start = (int(self.rect.centerx / CELL_SIZE), int(self.rect.centery / CELL_SIZE))
        goal = (int(self.last_player_pos[0] / CELL_SIZE), int(self.last_player_pos[1] / CELL_SIZE))
        
        if start == goal:
            return []
            
        # Erstelle Gitter für A*
        grid = [[0 for _ in range(len(MAZE_LAYOUT[0]))] for _ in range(len(MAZE_LAYOUT))]
        for wall in walls:
            grid_x = wall['pos'][0] // CELL_SIZE
            grid_y = wall['pos'][1] // CELL_SIZE
            if 0 <= grid_x < len(grid[0]) and 0 <= grid_y < len(grid):
                grid[grid_y][grid_x] = 1
        
        # A* Implementierung
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            # Nachbarn prüfen (inkl. Diagonalen)
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                next_x = current[0] + dx
                next_y = current[1] + dy
                
                # Prüfe Grenzen und Wände
                if (0 <= next_x < len(grid[0]) and 
                    0 <= next_y < len(grid) and 
                    grid[next_y][next_x] == 0):
                    
                    # Diagonale Bewegung nur erlauben, wenn beide angrenzenden Felder frei sind
                    if abs(dx) == 1 and abs(dy) == 1:
                        if grid[current[1]][current[0] + dx] == 1 or grid[current[1] + dy][current[0]] == 1:
                            continue
                    
                    next_pos = (next_x, next_y)
                    # Diagonale Bewegung kostet mehr
                    movement_cost = 1.4 if (abs(dx) == 1 and abs(dy) == 1) else 1
                    new_cost = cost_so_far[current] + movement_cost
                    
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        # Manhattan-Distanz als Heuristik
                        priority = new_cost + abs(goal[0] - next_x) + abs(goal[1] - next_y)
                        heapq.heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current
        
        # Pfad rekonstruieren
        path = []
        current = goal
        while current and current in came_from:
            # Füge Mittelpunkt der Zelle zum Pfad hinzu
            path.append((current[0] * CELL_SIZE + CELL_SIZE // 2,
                       current[1] * CELL_SIZE + CELL_SIZE // 2))
            current = came_from[current]
        
        path.reverse()
        return path

    def draw(self, screen):
        if not self.active:
            return
            
        # Draw the boss image using visual_rect
        screen.blit(self.image, (self.visual_rect.x + GAME_OFFSET_X, self.visual_rect.y + GAME_OFFSET_Y))
        
        # Draw the name above
        name_text = self.name_font.render(self.name, True, self.image.get_at((0, 0)))
        name_rect = name_text.get_rect(centerx=self.visual_rect.centerx + GAME_OFFSET_X, bottom=self.visual_rect.top + GAME_OFFSET_Y - 2)
        screen.blit(name_text, name_rect)
        
        # Debug: Draw hitbox in the boss's color
        pygame.draw.rect(screen, self.image.get_at((0, 0)), (self.rect.x + GAME_OFFSET_X, self.rect.y + GAME_OFFSET_Y, self.rect.width, self.rect.height), 1)
        # Debug: Draw center point
        center_x = self.rect.centerx + GAME_OFFSET_X
        center_y = self.rect.centery + GAME_OFFSET_Y
        pygame.draw.circle(screen, self.image.get_at((0, 0)), (center_x, center_y), 2)

class Letter:
    def __init__(self, x, y, letter):
        self.x = x
        self.y = y
        self.letter = letter
        self.font = pygame.font.Font(None, 36)
        self.collected = False
        self.rect = pygame.Rect(x, y, LETTER_SIZE, LETTER_SIZE)
        
        
        self.text_surface = self.font.render(letter, True, WHITE)
        self.text_rect = self.text_surface.get_rect(center=(x + LETTER_SIZE//2, y + LETTER_SIZE//2))

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.text_surface, (self.text_rect.x + GAME_OFFSET_X, self.text_rect.y + GAME_OFFSET_Y))

class CollectionDisplay:
    def __init__(self, language, difficulty):
        self.font = pygame.font.Font(None, 36)
        self.language = language
        self.collected_letters = []
        self.target_word = DIFFICULTY_SETTINGS[difficulty]['letters']
        self.letter_positions = {}
        self.hint_font = pygame.font.Font(None, 24)
        self.collected_positions = set()  # Neue Variable für gesammelte Positionen

        # Initialisiere die Buchstabenpositionen
        for i, letter in enumerate(self.target_word):
            if letter not in self.letter_positions:
                self.letter_positions[letter] = []
            self.letter_positions[letter].append(i)
        print(f"Buchstabenpositionen: {self.letter_positions}")  # Debug

    def add_letter(self, letter):
        # Finde die nächste unbenutzte Position für diesen Buchstaben
        positions = self.letter_positions.get(letter, [])
        for pos in positions:
            if pos not in self.collected_positions:
                self.collected_positions.add(pos)
                self.collected_letters.append((letter, pos))
                break
        
        # Sortiere nach Position
        self.collected_letters.sort(key=lambda x: x[1])
        
        # Debug-Ausgabe
        print(f"Füge Buchstabe hinzu: {letter}")
        print(f"Gesammelte Buchstaben: {[l[0] for l in self.collected_letters]}")

    def draw(self, screen):
        # Zeichne gesammelte Buchstaben
        collected_text = "".join(letter[0] for letter in self.collected_letters)
        text_surface = self.font.render(collected_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(DISPLAY_WIDTH // 2, 30))
        screen.blit(text_surface, text_rect)

        # Zeichne Fortschrittsanzeige
        hint_text = f"{len(self.collected_letters)}/{len(self.target_word)}"
        hint_surface = self.hint_font.render(hint_text, True, WHITE)
        hint_rect = hint_surface.get_rect(center=(DISPLAY_WIDTH // 2, 60))
        screen.blit(hint_surface, hint_rect)

class Timer:
    def __init__(self, total_seconds):
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.font = pygame.font.Font(None, 48)
        self.last_update = time.time()

    def update(self):
        current_time = time.time()
        self.remaining_seconds -= (current_time - self.last_update)
        self.last_update = current_time

    def draw(self, screen):
        minutes = int(self.remaining_seconds // 60)
        seconds = int(self.remaining_seconds % 60)
        text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
        # Draw at bottom right corner
        text_rect = text.get_rect(bottomright=(DISPLAY_WIDTH - 20, DISPLAY_HEIGHT - 20))
        screen.blit(text, text_rect)

class LanguageMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.languages = ['de', 'en']
        self.selected_index = 0
        
        # Controller Setup
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            
            joystick.init()
        
        # Zeitverzögerung für Joystick-Eingaben
        self.last_joy_time = 0
        self.joy_delay = 200  # Millisekunden
    
    def handle_input(self):
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Tastatureingaben
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.languages)
                elif event.key == K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.languages)
                elif event.key in (K_RETURN, K_SPACE):
                    return self.languages[self.selected_index]
            
            # Controller-Eingaben
            elif event.type == JOYBUTTONDOWN:
                if event.button == 0:  # X-Button (PS4)
                    return self.languages[self.selected_index]
            elif event.type == JOYAXISMOTION:
                if current_time - self.last_joy_time > self.joy_delay:
                    if event.axis == 1:  # Vertikale Achse
                        if event.value > 0.5:  # Nach unten
                            self.selected_index = (self.selected_index + 1) % len(self.languages)
                            self.last_joy_time = current_time
                        elif event.value < -0.5:  # Nach oben
                            self.selected_index = (self.selected_index - 1) % len(self.languages)
                            self.last_joy_time = current_time
            elif event.type == JOYHATMOTION:
                if current_time - self.last_joy_time > self.joy_delay:
                    hat = event.value
                    if hat[1] == 1:  # Nach oben
                        self.selected_index = (self.selected_index - 1) % len(self.languages)
                        self.last_joy_time = current_time
                    elif hat[1] == -1:  # Nach unten
                        self.selected_index = (self.selected_index + 1) % len(self.languages)
                        self.last_joy_time = current_time
        
        return None
    
    def run(self):
        while True:
            result = self.handle_input()
            if result is not None:
                return result
            
            self.screen.fill(BLACK)
            
            # Titel
            title_font = pygame.font.Font(None, 74)
            title = title_font.render('Select Language', True, WHITE)
            title_rect = title.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//4))
            self.screen.blit(title, title_rect)
            
            # Sprachoptionen
            for i, lang in enumerate(self.languages):
                color = WHITE if i == self.selected_index else GRAY
                text = pygame.font.Font(None, 48).render(TRANSLATIONS[lang]['language_name'], True, color)
                rect = text.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + i * 60))
                
                if i == self.selected_index:
                    pygame.draw.rect(self.screen, color, rect.inflate(20, 10), 2)
                
                self.screen.blit(text, rect)
            
            # Steuerungshinweise
            hint_font = pygame.font.Font(None, 36)
            keyboard_hint = hint_font.render('Press ENTER to select', True, GRAY)
            controller_hint = hint_font.render('Press X button to select', True, GRAY)
            
            keyboard_rect = keyboard_hint.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT * 3//4))
            controller_rect = controller_hint.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT * 3//4 + 40))
            
            self.screen.blit(keyboard_hint, keyboard_rect)
            self.screen.blit(controller_hint, controller_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

class CharacterMenu:
    def __init__(self, screen, clock, language):
        self.screen = screen
        self.clock = clock
        self.language = language
        self.character_names = ['Jonas', 'Robert', 'Sebastian']
        self.selected_index = 0
        
        # Menüoptionen erstellen - perfekt zentriert
        self.menu_options = [
            MenuOption(name, (DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 - 60 + i * 60))
            for i, name in enumerate(self.character_names)
        ]
        self.menu_options[self.selected_index].is_selected = True
        
        # Controller Setup
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            joystick.init()
        
        # Zeitverzögerung für Joystick-Eingaben
        self.last_joy_time = 0
        self.joy_delay = 200  # Millisekunden
    
    def handle_input(self):
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Tastatureingaben
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.menu_options[self.selected_index].is_selected = False
                    self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                    self.menu_options[self.selected_index].is_selected = True
                elif event.key == K_DOWN:
                    self.menu_options[self.selected_index].is_selected = False
                    self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                    self.menu_options[self.selected_index].is_selected = True
                elif event.key in (K_RETURN, K_SPACE):
                    return self.character_names[self.selected_index]
            
            # Controller-Eingaben
            elif event.type == JOYBUTTONDOWN:
                if event.button == 0:  # X-Button (PS4)
                    return self.character_names[self.selected_index]
            elif event.type == JOYAXISMOTION:
                if current_time - self.last_joy_time > self.joy_delay:
                    if event.axis == 1:  # Vertikale Achse
                        if event.value > 0.5:  # Nach unten
                            self.menu_options[self.selected_index].is_selected = False
                            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                            self.menu_options[self.selected_index].is_selected = True
                            self.last_joy_time = current_time
                        elif event.value < -0.5:  # Nach oben
                            self.menu_options[self.selected_index].is_selected = False
                            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                            self.menu_options[self.selected_index].is_selected = True
                            self.last_joy_time = current_time
            elif event.type == JOYHATMOTION:
                if current_time - self.last_joy_time > self.joy_delay:
                    hat = event.value
                    if hat[1] == 1:  # Nach oben
                        self.menu_options[self.selected_index].is_selected = False
                        self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                        self.menu_options[self.selected_index].is_selected = True
                        self.last_joy_time = current_time
                    elif hat[1] == -1:  # Nach unten
                        self.menu_options[self.selected_index].is_selected = False
                        self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                        self.menu_options[self.selected_index].is_selected = True
                        self.last_joy_time = current_time
        
        return None
    
    def run(self):
        while True:
            result = self.handle_input()
            if result is not None:
                return result
            
            self.screen.fill(BLACK)
            
            # Titel
            title_font = pygame.font.Font(None, 74)
            title = title_font.render(TRANSLATIONS[self.language]['select_character'], True, WHITE)
            title_rect = title.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//4))
            self.screen.blit(title, title_rect)
            
            # Menüoptionen
            for option in self.menu_options:
                option.draw(self.screen)
            
            # Steuerungshinweise
            hint_font = pygame.font.Font(None, 36)
            keyboard_hint = hint_font.render(TRANSLATIONS[self.language]['press_to_select'], True, GRAY)
            controller_hint = hint_font.render(TRANSLATIONS[self.language]['press_x_to_select'], True, GRAY)
            
            keyboard_rect = keyboard_hint.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT * 3//4))
            controller_rect = controller_hint.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT * 3//4 + 40))
            
            self.screen.blit(keyboard_hint, keyboard_rect)
            self.screen.blit(controller_hint, controller_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

class MenuOption:
    def __init__(self, text, position, size=(200, 50)):
        self.text = text
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.pos = position  # Position für zentrierte Textdarstellung
        self.is_selected = False
        self.font = pygame.font.Font(None, 48)

    def draw(self, screen):
        color = WHITE if self.is_selected else GRAY
        text = self.font.render(self.text, True, color)
        text_rect = text.get_rect(center=self.pos)
        
        if self.is_selected:
            pygame.draw.rect(screen, color, text_rect.inflate(20, 10), 2)
        
        screen.blit(text, text_rect)

def create_maze():
    walls = []
    paths = []  # Liste für Wege hinzugefügt
    for y in range(len(MAZE_LAYOUT)):
        for x in range(len(MAZE_LAYOUT[0])):
            pos_x = x * CELL_SIZE
            pos_y = y * CELL_SIZE
            
            if MAZE_LAYOUT[y][x] == 1:  # Wand
                walls.append({
                    'pos': (pos_x, pos_y),
                    'rect': pygame.Rect(pos_x, pos_y, CELL_SIZE, CELL_SIZE)  # Ohne GAME_OFFSET
                })
            else:  # Weg
                paths.append({
                    'pos': (pos_x, pos_y),
                    'rect': pygame.Rect(pos_x, pos_y, CELL_SIZE, CELL_SIZE)  # Ohne GAME_OFFSET
                })
    
    return walls, paths

def create_bosses(difficulty, boss_images):
    num_bosses = DIFFICULTY_SETTINGS[difficulty]['num_bosses']
    boss_speeds = DIFFICULTY_SETTINGS[difficulty]['speeds']
    bosses = []
    
    # Definiere die Startpositionen für die Bosse
    boss_starts = [
        (18 * CELL_SIZE, 18 * CELL_SIZE),  # Unten rechts
        (1 * CELL_SIZE, 18 * CELL_SIZE),   # Unten links
        (18 * CELL_SIZE, 1 * CELL_SIZE),   # Oben rechts
        (1 * CELL_SIZE, 1 * CELL_SIZE)     # Oben links
    ]
    
    # Definiere die Boss-Konfigurationen (nur 3 Bosse: Tom, Jannik, Louis)
    boss_configs = [
        {'name': 'Louis', 'speed': boss_speeds['fastest'], 'image': boss_images['red'], 'spawn_time': 1},
        {'name': 'Jannik', 'speed': boss_speeds['normal'], 'image': boss_images['blue'], 'spawn_time': 10},
        {'name': 'Tom', 'speed': boss_speeds['faster'], 'image': boss_images['green'], 'spawn_time': 20}
    ]
    
    # Erstelle die ausgewählte Anzahl an Bossen
    for i in range(num_bosses):
        if i < len(boss_starts) and i < len(boss_configs):
            config = boss_configs[i]
            x, y = boss_starts[i]
            boss = Boss(x, y, config['name'], config['speed'], config['image'], config['spawn_time'], difficulty)
            bosses.append(boss)
    
    return bosses

def create_letters(difficulty):
    letters = []
    target_word = DIFFICULTY_SETTINGS[difficulty]['letters']
    print(f"Zielwort: {target_word} (Länge: {len(target_word)})")  # Debug
    
    # Finde alle verfügbaren Positionen
    available_positions = []
    for y in range(len(MAZE_LAYOUT)):
        for x in range(len(MAZE_LAYOUT[0])):
            if MAZE_LAYOUT[y][x] == 0:  # Wenn es ein Weg ist
                # Mindestabstand zum Spielerstart (3 Felder)
                start_x = int(1.5 * CELL_SIZE)
                start_y = int(1.5 * CELL_SIZE)
                pos_x = x * CELL_SIZE
                pos_y = y * CELL_SIZE
                if abs(pos_x - start_x) > CELL_SIZE * 3 or abs(pos_y - start_y) > CELL_SIZE * 3:
                    available_positions.append((pos_x, pos_y))
    
    print(f"Verfügbare Positionen: {len(available_positions)}")  # Debug
    
    # Wähle zufällige Positionen für jeden Buchstaben
    for i, char in enumerate(target_word):
        if available_positions:
            pos = random.choice(available_positions)
            available_positions.remove(pos)
            letters.append({
                'char': char,
                'x': pos[0],
                'y': pos[1],
                'collected': False
            })
            print(f"Platziere Buchstabe {char} an Position {pos}")  # Debug
    
    print(f"Platzierte Buchstaben: {len(letters)}")  # Debug
    return letters

def check_letter_collection(player, letters, collection_display):
    for letter in letters[:]:  # Kopie der Liste zum Iterieren
        letter_rect = pygame.Rect(
            letter['x'],  # Ohne GAME_OFFSET
            letter['y'],  # Ohne GAME_OFFSET
            LETTER_SIZE,
            LETTER_SIZE
        )
        if not letter['collected'] and player.rect.colliderect(letter_rect):
            letter['collected'] = True
            collection_display.add_letter(letter['char'])
            letters.remove(letter)
            print(f"Buchstabe gesammelt: {letter['char']}")  # Debug

def check_boss_collision(player, bosses):
    player_rect = pygame.Rect(
        player.rect.x + GAME_OFFSET_X,
        player.rect.y + GAME_OFFSET_Y,
        player.rect.width,
        player.rect.height
    )
    
    for boss in bosses:
        if not boss.active:
            continue
            
        boss_rect = pygame.Rect(
            boss.rect.x + GAME_OFFSET_X,
            boss.rect.y + GAME_OFFSET_Y,
            boss.rect.width,
            boss.rect.height
        )
        
        if player_rect.colliderect(boss_rect):
            return True
    
    return False

def load_images():
    # Lade die Spielerbilder
    player_images = {}
    try:
        player_images = {
            'Jonas': pygame.transform.scale(pygame.image.load('images/jonas.png'), (PLAYER_SIZE, PLAYER_SIZE)),
            'Robert': pygame.transform.scale(pygame.image.load('images/robert.png'), (PLAYER_SIZE, PLAYER_SIZE)),
            'Sebastian': pygame.transform.scale(pygame.image.load('images/sebastian.png'), (PLAYER_SIZE, PLAYER_SIZE))
        }
    except:
        print("Warnung: Spielerbilder konnten nicht geladen werden, verwende Ersatzbilder")
        # Ersatzbilder
        player_images = {
            'Jonas': pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)),
            'Robert': pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)),
            'Sebastian': pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        }
        player_images['Jonas'].fill(BLUE)
        player_images['Robert'].fill(GREEN)
        player_images['Sebastian'].fill(YELLOW)
    
    # Lade Boss-Bilder
    boss_images = {}
    try:
        boss_images = {
            'red': pygame.transform.scale(pygame.image.load('images/louis.png'), (BOSS_SIZE, BOSS_SIZE)),
            'blue': pygame.transform.scale(pygame.image.load('images/jannik.png'), (BOSS_SIZE, BOSS_SIZE)),
            'green': pygame.transform.scale(pygame.image.load('images/tom.png'), (BOSS_SIZE, BOSS_SIZE)),
            'purple': pygame.transform.scale(pygame.image.load('images/phillip.png'), (BOSS_SIZE, BOSS_SIZE))
        }
    except:
        print("Warnung: Boss-Bilder konnten nicht geladen werden, verwende Ersatzbilder")
        # Ersatzbilder
        boss_images = {
            'red': pygame.Surface((BOSS_SIZE, BOSS_SIZE)),
            'blue': pygame.Surface((BOSS_SIZE, BOSS_SIZE)),
            'green': pygame.Surface((BOSS_SIZE, BOSS_SIZE)),
            'purple': pygame.Surface((BOSS_SIZE, BOSS_SIZE))
        }
        boss_images['red'].fill(RED)
        boss_images['blue'].fill(BLUE)
        boss_images['green'].fill(GREEN)
        boss_images['purple'].fill(PURPLE)

    # Lade Wand- und Weg-Texturen
    wall_img = None
    path_img = None
    try:
        wall_img = pygame.transform.scale(pygame.image.load('images/wall.png'), (CELL_SIZE, CELL_SIZE))
        path_img = pygame.transform.scale(pygame.image.load('images/path.png'), (CELL_SIZE, CELL_SIZE))
    except:
        print("Warnung: Wand/Weg-Bilder konnten nicht geladen werden, verwende Ersatzbilder")
        wall_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
        wall_img.fill(GRAY)
        path_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
        path_img.fill(BLACK)
    
    return player_images, boss_images, wall_img, path_img

def draw_game(screen, walls, paths, player, bosses, letters, collection_display, timer, language, difficulty, wall_img, path_img, boss_images, game_over=False, game_over_reason=None):
    screen.fill(BLACK)
    
    # Calculate player center in grid coordinates
    player_grid_x = player.x // CELL_SIZE
    player_grid_y = player.y // CELL_SIZE
    player_center_x = player.x + PLAYER_SIZE // 2
    player_center_y = player.y + PLAYER_SIZE // 2
    
    # Draw visible walls
    for wall in walls:
        wall_grid_x = wall['pos'][0] // CELL_SIZE
        wall_grid_y = wall['pos'][1] // CELL_SIZE
        
        # Check if wall is within vision radius
        if abs(wall_grid_x - player_grid_x) <= VISION_RADIUS and \
           abs(wall_grid_y - player_grid_y) <= VISION_RADIUS:
            screen.blit(wall_img, (wall['pos'][0] + GAME_OFFSET_X, wall['pos'][1] + GAME_OFFSET_Y))
    
    # Draw visible paths
    for path in paths:
        path_grid_x = path['pos'][0] // CELL_SIZE
        path_grid_y = path['pos'][1] // CELL_SIZE
        
        # Check if path is within vision radius
        if abs(path_grid_x - player_grid_x) <= VISION_RADIUS and \
           abs(path_grid_y - player_grid_y) <= VISION_RADIUS:
            screen.blit(path_img, (path['pos'][0] + GAME_OFFSET_X, path['pos'][1] + GAME_OFFSET_Y))
    
    # Draw visible letters
    for letter in letters:
        letter_grid_x = letter['x'] // CELL_SIZE
        letter_grid_y = letter['y'] // CELL_SIZE
        
        if abs(letter_grid_x - player_grid_x) <= VISION_RADIUS and \
           abs(letter_grid_y - player_grid_y) <= VISION_RADIUS:
            letter_rect = pygame.Rect(letter['x'] + GAME_OFFSET_X, letter['y'] + GAME_OFFSET_Y, LETTER_SIZE, LETTER_SIZE)
            letter_font = pygame.font.Font(None, 36)
            letter_text = letter_font.render(letter['char'], True, WHITE)
            letter_text_rect = letter_text.get_rect(center=letter_rect.center)
            screen.blit(letter_text, letter_text_rect)
    
    # Draw player
    player.draw(screen)
    
    # Draw active bosses
    for boss in bosses:
        if boss.active:
            boss.draw(screen)
    
    # Draw collection display
    collection_display.draw(screen)
    
    # Draw timer
    timer.draw(screen)
    
    if not game_over:
        # Create circular vision area
        vision_radius_px = VISION_RADIUS * CELL_SIZE
        vision_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        vision_surface.fill((0, 0, 0, FOG_ALPHA))  # Semi-transparent black
        
        # Create a circle mask for the vision
        pygame.draw.circle(vision_surface, (0, 0, 0, 0),
                         (int(player_center_x + GAME_OFFSET_X), 
                          int(player_center_y + GAME_OFFSET_Y)),
                          vision_radius_px)
        
        # Apply the fog of war
        screen.blit(vision_surface, (0, 0))
    
    # Draw game title instead of difficulty
    font = pygame.font.Font(None, 36)
    title_text = "Weidmüller Escape Game"
    title_surface = font.render(title_text, True, WHITE)
    title_rect = title_surface.get_rect(bottomleft=(20, DISPLAY_HEIGHT - 20))
    screen.blit(title_surface, title_rect)
    
    if game_over:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        font = pygame.font.Font(None, 74)
        if game_over_reason == 'win':
            text = font.render("Escape Successful!", True, GREEN)
        else:
            text = font.render("Game Over!", True, RED)
        
        text_rect = text.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 100))
        screen.blit(text, text_rect)
        
        if game_over_reason == 'win':
            question = font.render("Wo ist der Hauptsitz von Weidmüller?", True, WHITE)
            answer = font.render("DETMOLD", True, WHITE)
            
            question_rect = question.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
            answer_rect = answer.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 100))
            
            screen.blit(question, question_rect)
            screen.blit(answer, answer_rect)
    
    pygame.display.flip()

def play_game(screen, game_surface, clock, difficulty, player_image, boss_images, wall_img, path_img, language):
    # Initialisiere Spielobjekte
    walls, paths = create_maze()
    player = Player(CELL_SIZE, CELL_SIZE, player_image)
    bosses = create_bosses(difficulty, boss_images)
    letters = create_letters(difficulty)
    collection_display = CollectionDisplay(language, difficulty)
    timer = Timer(DIFFICULTY_SETTINGS[difficulty]['time_limit'])
    
    game_over = False
    game_over_reason = None
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
        
        # Update game state
        player.handle_input(walls)
        
        # Update bosses
        current_time = time.time()
        for boss in bosses:
            if current_time >= boss.spawn_time:
                boss.update(player, walls)
                
                # Check for collision with boss
                if boss.rect.colliderect(player.rect):
                    game_over = True
                    game_over_reason = 'caught'
                    break
        
        # Check letter collection
        for letter in letters[:]:  # Kopie der Liste zum Iterieren
            letter_rect = pygame.Rect(
                letter['x'],  # Ohne GAME_OFFSET
                letter['y'],  # Ohne GAME_OFFSET
                LETTER_SIZE,
                LETTER_SIZE
            )
            if not letter['collected'] and player.rect.colliderect(letter_rect):
                letter['collected'] = True
                collection_display.add_letter(letter['char'])
                letters.remove(letter)
                print(f"Buchstabe gesammelt: {letter['char']}")  # Debug
        
        # Update timer
        timer.update()
        if timer.remaining_seconds <= 0:
            game_over = True
            game_over_reason = 'time_up'
        
        # Check win condition
        if len(collection_display.collected_letters) == len(DIFFICULTY_SETTINGS[difficulty]['letters']):
            game_over = True
            game_over_reason = 'win'
        
        # Draw everything
        game_surface.fill(BLACK)
        draw_game(game_surface, walls, paths, player, bosses, letters, collection_display, timer, language, difficulty, wall_img, path_img, boss_images, game_over, game_over_reason)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    return game_over_reason

def get_default_difficulty():
    """Returns the default difficulty setting"""
    return 'medium'

def show_game_over(screen, clock, game_over_reason, language):
    font = pygame.font.Font(None, 74)
    
    # Text basierend auf Spielende-Grund mit Fehlerbehandlung
    try:
        if game_over_reason == 'caught':
            text = TRANSLATIONS[language]['caught_by_boss']
        elif game_over_reason == 'time_up':
            text = TRANSLATIONS[language]['time_up']
        elif game_over_reason == 'win':
            text = TRANSLATIONS[language]['you_won']
        else:
            text = TRANSLATIONS[language]['game_over']
    except KeyError:
        # Fallback text if translation is missing
        if game_over_reason == 'caught':
            text = "Caught by Boss!"
        elif game_over_reason == 'time_up':
            text = "Time is up!"
        elif game_over_reason == 'win':
            text = "You Won!"
        else:
            text = "Game Over!"
    
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//3))
    
    # Bei Gewinn zeige das Lösungswort und die Frage an
    if game_over_reason == 'win':
        # Zeige die Frage
        question_font = pygame.font.Font(None, 48)
        try:
            question_text = TRANSLATIONS[language]['question']
        except KeyError:
            question_text = "Where is the headquarters of Weidmüller?"
        question_surface = question_font.render(question_text, True, WHITE)
        question_rect = question_surface.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2))
        
        # Zeige "Die Antwort ist:"
        answer_label_font = pygame.font.Font(None, 36)
        try:
            answer_label = TRANSLATIONS[language]['answer']
        except KeyError:
            answer_label = "The answer is:"
        answer_label_surface = answer_label_font.render(answer_label, True, WHITE)
        answer_label_rect = answer_label_surface.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + 40))
        
        # Zeige das Lösungswort
        answer_font = pygame.font.Font(None, 64)
        answer_text = "DETMOLD"
        answer_surface = answer_font.render(answer_text, True, YELLOW)
        answer_rect = answer_surface.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + 80))
    
    # Hinweis zum Neustart
    hint_font = pygame.font.Font(None, 36)
    try:
        hint_text = TRANSLATIONS[language]['press_to_restart']
    except KeyError:
        hint_text = "Press ENTER or X button to restart"
    hint_surface = hint_font.render(hint_text, True, GRAY)
    hint_rect = hint_surface.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT * 4//5))
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key in (K_RETURN, K_SPACE):
                    waiting = False
            elif event.type == JOYBUTTONDOWN:
                if event.button == 0:  # X-Button (PS4)
                    waiting = False
        
        screen.fill(BLACK)
        screen.blit(text_surface, text_rect)
        
        # Zeige Frage und Antwort nur bei Gewinn
        if game_over_reason == 'win':
            screen.blit(question_surface, question_rect)
            screen.blit(answer_label_surface, answer_label_rect)
            screen.blit(answer_surface, answer_rect)
        
        screen.blit(hint_surface, hint_rect)
        pygame.display.flip()
        clock.tick(60)

class LoadingScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.duration = 5.0  # 5 Sekunden
        self.start_time = None
        
        # Kein Logo mehr - nur Loading Screen
        self.logo = None
    

    
    def run(self):
        """Zeigt den Loading Screen für 5 Sekunden"""
        self.start_time = time.time()
        
        while True:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            
            # Prüfe ob 5 Sekunden vergangen sind
            if elapsed_time >= self.duration:
                break
            
            # Event-Handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return  
            
            # Zeichne Loading Screen
            self.screen.fill(BLACK)
            
            # Zeichne Loading-Animation
            self.draw_loading_animation(elapsed_time)
            
            # Zeichne "Loading..." Text
            loading_font = pygame.font.Font(None, 48)
            loading_text = loading_font.render("Loading...", True, WHITE)
            loading_rect = loading_text.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + 150))
            self.screen.blit(loading_text, loading_rect)
            
            # Zeichne verbleibende Zeit
            remaining_time = max(0, self.duration - elapsed_time)
            time_font = pygame.font.Font(None, 36)
            time_text = time_font.render(f"{remaining_time:.1f}s", True, GRAY)
            time_rect = time_text.get_rect(center=(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + 200))
            self.screen.blit(time_text, time_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def draw_loading_animation(self, elapsed_time):
        """Zeichnet eine einfache Loading-Animation"""
        # Erstelle animierte Punkte
        num_dots = 3
        dot_radius = 8
        spacing = 30
        total_width = (num_dots - 1) * spacing
        start_x = DISPLAY_WIDTH//2 - total_width//2
        
        for i in range(num_dots):
            # Berechne Animation basierend auf Zeit
            animation_offset = (elapsed_time * 2 + i * 0.5) % 2
            alpha = int(128 + 127 * math.sin(animation_offset * math.pi))
            
            # Erstelle eine Surface für den animierten Punkt
            dot_surface = pygame.Surface((dot_radius * 2, dot_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (255, 255, 255, alpha), (dot_radius, dot_radius), dot_radius)
            
            # Position des Punktes
            x = start_x + i * spacing
            y = DISPLAY_HEIGHT//2 + 100
            
            self.screen.blit(dot_surface, (x - dot_radius, y - dot_radius))

def main():
    pygame.init()
    pygame.joystick.init()
    
    # Vollbildmodus aktivieren
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Escape Room Labyrinth")
    
    clock = pygame.time.Clock()
    
    # Controller initialisieren
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()
    
    # Load images
    player_images, boss_images, wall_img, path_img = load_images()
    
    language_menu = LanguageMenu(screen, clock)
    language = language_menu.run()
    
    character_menu = CharacterMenu(screen, clock, language)
    character = character_menu.run()
    
    # Loading Screen anzeigen
    loading_screen = LoadingScreen(screen, clock)
    loading_screen.run()

    while True:  
        difficulty = get_default_difficulty()  # Verwende feste Schwierigkeit
        
        # Spiel starten
        game_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        game_over = play_game(screen, game_surface, clock, difficulty, player_images[character], boss_images, wall_img, path_img, language)
        
        if game_over:
            show_game_over(screen, clock, game_over, language)

if __name__ == '__main__':
    main()
