import pygame
import sys
import time
import random
import math
import heapq
from pygame.locals import *
from collections import defaultdict
from languages import TRANSLATIONS

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 32  # Adjusted to fit the new resolution
PLAYER_SIZE = int(CELL_SIZE * 0.8)
BOSS_SIZE = int(CELL_SIZE * 0.8)
LETTER_SIZE = 30
VISION_RADIUS = 3  # Reduzierte Sichtweite (war vorher größer)
FOG_ALPHA = 200   # Dunklerer Nebel
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
            'normal': 1,    # Slower
            'fast': 1.5,    # Slower
            'faster': 2,    # Slower
            'fastest': 2.5  # Slower
        },
        'time_limit': 600,  # 10 minutes
        'letters': "DETMOLD",
        'num_bosses': 2  # Weniger Bosse im Easy-Modus
    },
    'medium': {
        'speeds': {
            'normal': 1.5,
            'fast': 2,
            'faster': 2.5,
            'fastest': 3
        },
        'time_limit': 420,  # 7 minutes
        'letters': "DETMOLD",
        'num_bosses': 3  # Mittlere Anzahl Bosse
    },
    'hard': {
        'speeds': {
            'normal': 2,
            'fast': 2.5,
            'faster': 3,
            'fastest': 3.5
        },
        'time_limit': 300,  # 5 minutes
        'letters': "DETMOLD",
        'num_bosses': 4  # Alle Bosse im Hard-Modus
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

# Constants
WINDOW_WIDTH = len(MAZE_LAYOUT[0]) * CELL_SIZE
WINDOW_HEIGHT = len(MAZE_LAYOUT) * CELL_SIZE

class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        # Make hitbox even smaller (40% of visual size)
        hitbox_size = int(PLAYER_SIZE * 0.4)
        hitbox_offset = (PLAYER_SIZE - hitbox_size) // 2
        self.rect = pygame.Rect(x + hitbox_offset, y + hitbox_offset, hitbox_size, hitbox_size)
        self.visual_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = 2  # Reduced from 5 to 3
        self.interaction_cooldown = 0
        self.image = image
        self.last_move_time = time.time()
        self.move_delay = 0.01  # Add slight delay between movements

    def handle_input(self, walls):
        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            return

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Only allow one direction at a time for more precise control
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        if dx != 0 or dy != 0:
            self.move(dx, dy, walls)
            self.last_move_time = current_time

    def move(self, dx, dy, walls):
        # Move at constant speed
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
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
        screen.blit(self.image, self.visual_rect)
        # Debug: Draw hitbox in red
        pygame.draw.rect(screen, RED, self.rect, 1)

class Boss:
    def __init__(self, x, y, name, speed, image, spawn_time, difficulty='medium'):
        self.x = x
        self.y = y
        self.hitbox_size = int(BOSS_SIZE * 0.6)  # Kleinere Hitbox
        self.hitbox_offset = (BOSS_SIZE - self.hitbox_size) // 2
        self.rect = pygame.Rect(x + self.hitbox_offset, y + self.hitbox_offset, self.hitbox_size, self.hitbox_size)
        self.visual_rect = pygame.Rect(x, y, BOSS_SIZE, BOSS_SIZE)
        self.name = name
        self.speed = speed
        self.image = image
        self.spawn_time = spawn_time
        self.active = False
        self.name_font = pygame.font.Font(None, 20)
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30  # Längeres Intervall für Pfadaktualisierung
        self.last_player_pos = None
        self.difficulty = difficulty
        
    def update(self, player, walls):
        # Aktualisiere die Hitbox-Position
        self.rect.x = self.x + self.hitbox_offset
        self.rect.y = self.y + self.hitbox_offset
        self.visual_rect.x = self.x
        self.visual_rect.y = self.y
        
        # Prüfe ob der Boss aktiv sein soll
        if not self.active and time.time() >= self.spawn_time:
            self.active = True
        
        if not self.active:
            return
            
        # Aktualisiere den Pfad nur in bestimmten Intervallen
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval:
            self.path_update_timer = 0
            # Speichere die letzte bekannte Spielerposition
            self.last_player_pos = (player.rect.centerx, player.rect.centery)
            # Berechne neuen Pfad zum Spieler
            self.path = self.find_path_to_player(player, walls)
        
        # Bewege den Boss entlang des Pfades
        if self.path:
            next_x, next_y = self.path[0]
            dx = next_x - self.rect.centerx
            dy = next_y - self.rect.centery
            
            # Normalisiere die Bewegung
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                # Bewege den Boss
                new_x = self.x + dx
                new_y = self.y + dy
                
                # Prüfe Kollisionen mit Wänden
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
                    
                # Wenn wir nah genug am nächsten Wegpunkt sind, entferne ihn
                if distance < self.speed * 2:
                    self.path.pop(0)
    
    def find_path_to_player(self, player, walls):
        if not self.last_player_pos:
            return []
            
        # Vereinfachter A* Pathfinding-Algorithmus
        start = (int(self.rect.centerx / CELL_SIZE), int(self.rect.centery / CELL_SIZE))
        goal = (int(self.last_player_pos[0] / CELL_SIZE), int(self.last_player_pos[1] / CELL_SIZE))
        
        # Wenn Start und Ziel gleich sind, kein Pfad nötig
        if start == goal:
            return []
            
        # Erstelle ein vereinfachtes Gitter für die Pfadsuche
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
            current = frontier.pop(0)[1]
            
            if current == goal:
                break
                
            # Prüfe alle Nachbarn
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x = current[0] + dx
                next_y = current[1] + dy
                
                if (0 <= next_x < len(grid[0]) and 
                    0 <= next_y < len(grid) and 
                    grid[next_y][next_x] == 0):
                    
                    next_pos = (next_x, next_y)
                    new_cost = cost_so_far[current] + 1
                    
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + abs(goal[0] - next_x) + abs(goal[1] - next_y)
                        frontier.append((priority, next_pos))
                        frontier.sort()
                        came_from[next_pos] = current
        
        # Rekonstruiere den Pfad
        path = []
        current = goal
        while current and current in came_from:
            path.append((current[0] * CELL_SIZE + CELL_SIZE // 2,
                       current[1] * CELL_SIZE + CELL_SIZE // 2))
            current = came_from[current]
        
        path.reverse()
        return path

    def draw(self, screen):
        if not self.active:
            return
            
        # Draw the boss image using visual_rect
        screen.blit(self.image, self.visual_rect)
        
        # Draw the name above
        name_text = self.name_font.render(self.name, True, self.image.get_at((0, 0)))
        name_rect = name_text.get_rect(centerx=self.visual_rect.centerx, bottom=self.visual_rect.top - 2)
        screen.blit(name_text, name_rect)
        
        # Debug: Draw hitbox in the boss's color
        pygame.draw.rect(screen, self.image.get_at((0, 0)), self.rect, 1)
        # Debug: Draw center point
        center_x = self.rect.centerx
        center_y = self.rect.centery
        pygame.draw.circle(screen, self.image.get_at((0, 0)), (center_x, center_y), 2)

class Letter:
    def __init__(self, x, y, letter):
        self.x = x
        self.y = y
        self.letter = letter
        self.font = pygame.font.Font(None, 36)
        self.collected = False
        self.rect = pygame.Rect(x, y, LETTER_SIZE, LETTER_SIZE)
        
        # Erstelle die Textoberfläche
        self.text_surface = self.font.render(letter, True, WHITE)
        self.text_rect = self.text_surface.get_rect(center=(x + LETTER_SIZE//2, y + LETTER_SIZE//2))

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.text_surface, self.text_rect)

class CollectionDisplay:
    def __init__(self, language):
        self.font = pygame.font.Font(None, 36)
        self.language = language
        self.collected_letters = []
        self.target_word = DIFFICULTY_SETTINGS['easy']['letters']
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
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))
        screen.blit(text_surface, text_rect)

        # Zeichne Fortschrittsanzeige
        hint_text = f"{len(self.collected_letters)}/{len(self.target_word)}"
        hint_surface = self.hint_font.render(hint_text, True, WHITE)
        hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, 60))
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
        text_rect = text.get_rect(bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20))
        screen.blit(text, text_rect)

class LanguageSelector:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.languages = ['en', 'de']
        self.selected_index = 0
        self.font = pygame.font.Font(None, 48)

    def show(self):
        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.languages)
                    elif event.key == K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.languages)
                    elif event.key == K_RETURN:
                        selecting = False
                elif event.type == JOYBUTTONDOWN and event.button == 0:  
                    selecting = False
                elif event.type == JOYAXISMOTION:
                    if event.axis == 1:
                        if event.value < -0.5:
                            self.selected_index = (self.selected_index - 1) % len(self.languages)
                        elif event.value > 0.5:
                            self.selected_index = (self.selected_index + 1) % len(self.languages)

            self.screen.fill(BLACK)
            
            title_font = pygame.font.Font(None, 64)
            for lang in self.languages:
                title = title_font.render(TRANSLATIONS[lang]['select_language'], True, WHITE)
                title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
                self.screen.blit(title, title_rect)
                break  

            for i, lang in enumerate(self.languages):
                color = WHITE if i == self.selected_index else GRAY
                text = self.font.render(TRANSLATIONS[lang]['language_name'], True, color)
                rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + i * 60))
                
                if i == self.selected_index:
                    pygame.draw.rect(self.screen, color, rect.inflate(20, 10), 2)
                
                self.screen.blit(text, rect)

            instruction_font = pygame.font.Font(None, 36)
            for lang in self.languages:
                instruction = instruction_font.render(TRANSLATIONS[lang]['press_to_select'], True, GRAY)
                instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT * 3//4))
                self.screen.blit(instruction, instruction_rect)
                break  

            pygame.display.flip()
            self.clock.tick(60)

        return self.languages[self.selected_index]

class MenuOption:
    def __init__(self, text, position, size=(200, 50)):
        self.text = text
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.is_selected = False
        self.font = pygame.font.Font(None, 48)

    def draw(self, screen):
        color = WHITE if self.is_selected else GRAY
        pygame.draw.rect(screen, color, self.rect, 2)
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

def show_character_menu(screen, clock, language):
    menu_options = [
        MenuOption('Jonas', (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 60)),
        MenuOption('Robert', (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2)),
        MenuOption('Sebastian', (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 60))
    ]
    
    selected_option = 0
    menu_options[selected_option].is_selected = True
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    menu_options[selected_option].is_selected = False
                    selected_option = (selected_option - 1) % len(menu_options)
                    menu_options[selected_option].is_selected = True
                elif event.key == K_DOWN:
                    menu_options[selected_option].is_selected = False
                    selected_option = (selected_option + 1) % len(menu_options)
                    menu_options[selected_option].is_selected = True
                elif event.key == K_RETURN:
                    return menu_options[selected_option].text
            elif event.type == JOYBUTTONDOWN and event.button == 0:  
                return menu_options[selected_option].text
        
        screen.fill(BLACK)
        
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Wähle deinen Charakter", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        screen.blit(title, title_rect)
        
        for option in menu_options:
            option.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def create_maze():
    walls = []
    paths = []  # Liste für Wege hinzugefügt
    for row in range(len(MAZE_LAYOUT)):
        for col in range(len(MAZE_LAYOUT[0])):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            if MAZE_LAYOUT[row][col] == 1:
                walls.append({'rect': pygame.Rect(x, y, CELL_SIZE, CELL_SIZE), 'pos': (x, y)})
            else:
                paths.append({'rect': pygame.Rect(x, y, CELL_SIZE, CELL_SIZE), 'pos': (x, y)})
    return walls, paths

def create_letters(difficulty):
    letters = []
    target_word = DIFFICULTY_SETTINGS[difficulty]['letters']
    print(f"Zielwort: {target_word} (Länge: {len(target_word)})")
    available_positions = []
    
    # Finde alle verfügbaren Positionen (Wege)
    for y in range(len(MAZE_LAYOUT)):
        for x in range(len(MAZE_LAYOUT[0])):
            if MAZE_LAYOUT[y][x] == 0:  # Wenn es ein Weg ist
                pos_x = x * CELL_SIZE + (CELL_SIZE - LETTER_SIZE) // 2
                pos_y = y * CELL_SIZE + (CELL_SIZE - LETTER_SIZE) // 2
                
                # Überprüfe Mindestabstand zum Start (4 Felder)
                start_x = int(1.5 * CELL_SIZE)
                start_y = int(1.5 * CELL_SIZE)
                if abs(pos_x - start_x) > CELL_SIZE * 4 or abs(pos_y - start_y) > CELL_SIZE * 4:
                    available_positions.append((pos_x, pos_y))
    
    print(f"Verfügbare Positionen: {len(available_positions)}")
    
    # Mische die verfügbaren Positionen
    random.shuffle(available_positions)
    
    # Stelle sicher, dass wir genug Positionen haben
    if len(available_positions) < len(target_word):
        print(f"Warnung: Nicht genug Positionen ({len(available_positions)}) für alle Buchstaben ({len(target_word)})")
        return letters
    
    # Wähle zufällige Positionen für jeden Buchstaben
    selected_positions = random.sample(available_positions, len(target_word))
    
    # Platziere die Buchstaben
    for i, letter in enumerate(target_word):
        print(f"Platziere Buchstabe {i}: {letter}")
        letters.append(Letter(selected_positions[i][0], selected_positions[i][1], letter))
    
    print(f"Platzierte Buchstaben: {len(letters)}")
    return letters

def check_letter_collection(player, letters, collection_display):
    # Überprüfe Kollision mit Buchstaben
    for letter in letters:
        if not letter.collected and player.rect.colliderect(letter.rect):
            letter.collected = True
            collection_display.add_letter(letter.letter)
            letters.remove(letter)  # Entferne den gesammelten Buchstaben

def check_boss_collision(player, bosses):
    # Get player center point
    player_center = pygame.math.Vector2(player.rect.centerx, player.rect.centery)
    
    for boss in bosses:
        if not boss.active:
            continue
            
        # Get boss center point
        boss_center = pygame.math.Vector2(boss.rect.centerx, boss.rect.centery)
        
        # Calculate actual distance between centers
        distance = player_center.distance_to(boss_center)
        
        # Only count as collision if they're really close (25% of cell size)
        collision_threshold = CELL_SIZE * 0.25
        
        if distance < collision_threshold:
            return True
            
    return False

def create_bosses(difficulty, boss_images):
    bosses = []
    num_bosses = DIFFICULTY_SETTINGS[difficulty]['num_bosses']
    boss_names = ['Louis', 'Jannik', 'Tom', 'Phillip'][:num_bosses]  # Begrenzt auf die gewünschte Anzahl
    
    # Erstelle zufällige Startpositionen für die Bosse
    available_positions = []
    for y in range(len(MAZE_LAYOUT)):
        for x in range(len(MAZE_LAYOUT[0])):
            if MAZE_LAYOUT[y][x] == 0:  # Wenn es ein Weg ist
                pos_x = x * CELL_SIZE
                pos_y = y * CELL_SIZE
                # Mindestabstand zum Spielerstart (4 Felder)
                start_x = int(1.5 * CELL_SIZE)
                start_y = int(1.5 * CELL_SIZE)
                if abs(pos_x - start_x) > CELL_SIZE * 4 or abs(pos_y - start_y) > CELL_SIZE * 4:
                    available_positions.append((pos_x, pos_y))
    
    # Wähle zufällige Positionen für jeden Boss
    if available_positions:
        selected_positions = random.sample(available_positions, min(len(boss_names), len(available_positions)))
        for i, name in enumerate(boss_names):
            if i < len(selected_positions):
                x, y = selected_positions[i]
                speed_type = random.choice(['normal', 'fast', 'faster', 'fastest'])
                speed = DIFFICULTY_SETTINGS[difficulty]['speeds'][speed_type]
                # Staffele die Spawn-Zeiten (30 Sekunden Abstand)
                spawn_time = time.time() + (i * 30)
                bosses.append(Boss(x, y, name, speed, boss_images[name], spawn_time, difficulty))
    
    return bosses

def draw_game(screen, walls, player, bosses, letters, collection_display, timer, language, difficulty, game_over=False, game_over_reason=None, paths=None, wall_img=None, path_img=None, boss_images=None):
    # Draw background
    screen.fill(BLACK)
    
    # Calculate player center in grid coordinates
    player_center_x = player.x + PLAYER_SIZE // 2
    player_center_y = player.y + PLAYER_SIZE // 2
    player_grid_x = int(player_center_x // CELL_SIZE)
    player_grid_y = int(player_center_y // CELL_SIZE)
    
    # Draw visible walls and paths
    for wall in walls:
        wall_grid_x = wall['pos'][0] // CELL_SIZE
        wall_grid_y = wall['pos'][1] // CELL_SIZE
        
        # Check if wall is within vision radius
        if abs(wall_grid_x - player_grid_x) <= VISION_RADIUS and \
           abs(wall_grid_y - player_grid_y) <= VISION_RADIUS:
            screen.blit(wall_img, wall['pos'])
    
    # Draw visible paths
    if paths:  # Check if paths is not None
        for path in paths:
            path_grid_x = path['pos'][0] // CELL_SIZE
            path_grid_y = path['pos'][1] // CELL_SIZE
            
            # Check if path is within vision radius
            if abs(path_grid_x - player_grid_x) <= VISION_RADIUS and \
               abs(path_grid_y - player_grid_y) <= VISION_RADIUS:
                screen.blit(path_img, path['pos'])
    
    # Draw visible letters
    for letter in letters:
        letter_grid_x = letter.x // CELL_SIZE
        letter_grid_y = letter.y // CELL_SIZE
        
        if abs(letter_grid_x - player_grid_x) <= VISION_RADIUS and \
           abs(letter_grid_y - player_grid_y) <= VISION_RADIUS:
            letter.draw(screen)
    
    # Draw player
    player.draw(screen)
    
    # Draw active bosses only if in vision range
    for boss in bosses:
        if boss.active:
            boss_grid_x = int(boss.x // CELL_SIZE)
            boss_grid_y = int(boss.y // CELL_SIZE)
            
            if abs(boss_grid_x - player_grid_x) <= VISION_RADIUS and \
               abs(boss_grid_y - player_grid_y) <= VISION_RADIUS:
                boss.draw(screen)
    
    # Draw fog of war if game is not over
    if not game_over:
        # Create circular vision area
        vision_radius_px = VISION_RADIUS * CELL_SIZE
        vision_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        vision_surface.fill((0, 0, 0, FOG_ALPHA))  # Semi-transparent black
        
        # Create a circle mask for the vision
        pygame.draw.circle(vision_surface, (0, 0, 0, 0), 
                         (int(player_center_x), int(player_center_y)), 
                         vision_radius_px)
        
        # Apply the fog of war
        screen.blit(vision_surface, (0, 0))
    
    # Draw UI elements
    collection_display.draw(screen)
    timer.draw(screen)
    
    # Draw difficulty text
    font = pygame.font.Font(None, 36)
    difficulty_text = font.render(f"{TRANSLATIONS[language][difficulty]}", True, WHITE)
    difficulty_rect = difficulty_text.get_rect(bottomleft=(20, WINDOW_HEIGHT - 20))
    screen.blit(difficulty_text, difficulty_rect)
    
    if game_over:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        font = pygame.font.Font(None, 74)
        if game_over_reason == 'win':
            text = font.render("Escape Successful!", True, (0, 255, 0))  # Green text
            question = font.render("Der Hauptsitz liegt in?", True, WHITE)
            answer = font.render(collection_display.target_word, True, WHITE)
        else:
            text = font.render("Game Over!", True, (255, 0, 0))  # Red text
        
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(text, text_rect)
        
        if game_over_reason == 'win':
            question_rect = question.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(question, question_rect)
            answer_rect = answer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            screen.blit(answer, answer_rect)
    
    pygame.display.flip()

def show_menu(screen, clock, language):
    # Create menu options with translated text but return English keys
    translations = {
        TRANSLATIONS[language]['easy']: 'easy',
        TRANSLATIONS[language]['medium']: 'medium',
        TRANSLATIONS[language]['hard']: 'hard'
    }
    
    menu_options = [
        MenuOption(TRANSLATIONS[language]['easy'], (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 60)),
        MenuOption(TRANSLATIONS[language]['medium'], (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2)),
        MenuOption(TRANSLATIONS[language]['hard'], (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 60))
    ]
    
    selected_option = 0
    menu_options[selected_option].is_selected = True
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    menu_options[selected_option].is_selected = False
                    selected_option = (selected_option - 1) % len(menu_options)
                    menu_options[selected_option].is_selected = True
                elif event.key == K_DOWN:
                    menu_options[selected_option].is_selected = False
                    selected_option = (selected_option + 1) % len(menu_options)
                    menu_options[selected_option].is_selected = True
                elif event.key == K_RETURN:
                    return translations[menu_options[selected_option].text]
            elif event.type == JOYBUTTONDOWN and event.button == 0:  
                return translations[menu_options[selected_option].text]
        
        screen.fill(BLACK)
        
        title_font = pygame.font.Font(None, 64)
        title = title_font.render(TRANSLATIONS[language]['menu_title'], True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        screen.blit(title, title_rect)
        
        for option in menu_options:
            option.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def load_images():
    # Lade das Standard-Spielerbild für alle Charaktere
    player_img = pygame.image.load('images/player.png')
    player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
    
    # Verwende das gleiche Bild für alle Charaktere (vorübergehend)
    player_images = {
        'Jonas': player_img,
        'Robert': player_img,
        'Sebastian': player_img
    }
    
    # Lade Boss-Bilder
    boss_images = {
        'Louis': pygame.transform.scale(pygame.image.load('images/louis.png'), (BOSS_SIZE, BOSS_SIZE)),
        'Jannik': pygame.transform.scale(pygame.image.load('images/jannik.png'), (BOSS_SIZE, BOSS_SIZE)),
        'Tom': pygame.transform.scale(pygame.image.load('images/tom.png'), (BOSS_SIZE, BOSS_SIZE)),
        'Phillip': pygame.transform.scale(pygame.image.load('images/phillip.png'), (BOSS_SIZE, BOSS_SIZE))
    }

    # Lade Wand- und Weg-Texturen
    wall_img = pygame.image.load('images/wall.png')
    wall_img = pygame.transform.scale(wall_img, (CELL_SIZE, CELL_SIZE))
    path_img = pygame.image.load('images/path.png')
    path_img = pygame.transform.scale(path_img, (CELL_SIZE, CELL_SIZE))
    
    return player_images, boss_images, wall_img, path_img

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Weidmüller Escape Room Labyrinth')
    clock = pygame.time.Clock()
    
    # Load images
    player_images, boss_images, wall_img, path_img = load_images()
    
    language_selector = LanguageSelector(screen, clock)
    language = language_selector.show()
    
    character = show_character_menu(screen, clock, language)
    
    while True:  
        difficulty = show_menu(screen, clock, language)
        
        walls, paths = create_maze()
        player = Player(CELL_SIZE * 1.5, CELL_SIZE * 1.5, player_images[character])
        letters = create_letters(difficulty)
        collection_display = CollectionDisplay(language)
        timer = Timer(DIFFICULTY_SETTINGS[difficulty]['time_limit'])
        
        # Create bosses with different spawn times
        bosses = create_bosses(difficulty, boss_images)
        
        game_over = False
        game_over_reason = ""
        all_letters_collected = False
        restart_game = False
        
        start_time = time.time()
        while not restart_game:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if game_over:
                    if event.type == KEYDOWN and event.key == K_RETURN:
                        restart_game = True
            
            timer.update()
            
            if not game_over:
                # Handle player movement
                player.handle_input(walls)
                
                elapsed_time = time.time() - start_time
                for boss in bosses:
                    if elapsed_time >= boss.spawn_time:
                        boss.active = True
                    boss.update(player, walls)
                
                if check_boss_collision(player, bosses):
                    game_over = True
                    game_over_reason = 'caught_by_boss'
                
                check_letter_collection(player, letters, collection_display)
                
                if len(letters) == 0:
                    game_over = True
                    game_over_reason = 'win'
                    print("Spiel gewonnen!")  # Debug
                
                if timer.remaining_seconds <= 0:
                    game_over = True
                    game_over_reason = 'time_up'
                
            draw_game(screen, walls, player, bosses, letters, collection_display, timer, language, difficulty, game_over, game_over_reason, paths, wall_img, path_img, boss_images)
        
        # If we get here, the game is restarting
        if game_over_reason == 'win':
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # Draw win text
            font = pygame.font.Font(None, 74)
            text = font.render("Escape Successful!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
            screen.blit(text, text_rect)
            
            # Draw question and answer
            question = font.render("Der Hauptsitz liegt in?", True, WHITE)
            answer = font.render("DETMOLD", True, WHITE)
            
            question_rect = question.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            answer_rect = answer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            
            screen.blit(question, question_rect)
            screen.blit(answer, answer_rect)
            
            pygame.display.flip()
            
            # Warte 5 Sekunden oder bis Enter gedrückt wird
            start_time = time.time()
            waiting = True
            while waiting and time.time() - start_time < 5:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            waiting = False
                clock.tick(60)

if __name__ == '__main__':
    main()
