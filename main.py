import pygame
import random
import time
from pygame.locals import *
import os
from pyPS4Controller.controller import Controller

TILE_SIZE = 40
MAZE_WIDTH = 30
MAZE_HEIGHT = 30
VIEWPORT_WIDTH = 20
VIEWPORT_HEIGHT = 15
SCREEN_WIDTH = 800  # Raspberry Pi Touchscreen Breite
SCREEN_HEIGHT = 480  # Raspberry Pi Touchscreen Höhe

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)  # Leuchtendes Gelb für Boost-Symbol
WRONG_LETTER_COLOR = (255, 255, 255)  # Weiß
CORRECT_LETTER_COLOR = (255, 165, 0)  # Orange

player_pos = [1, 1]
player_lives = 3
shield_active = False
shield_timer = 0
shield_cooldown = 20
shield_duration = 10
shield_symbol = "U-Stahl"
boost_active = False
boost_timer = 0
boost_duration = 1.5  # Boost dauert 1,5 Sekunden
player_speed = 1
normal_speed = 1
boost_speed = 2

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Labyrinth with Letters (Raspberry Pi Touchscreen Edition)')
clock = pygame.time.Clock()

player_images = [
    pygame.transform.scale(pygame.image.load(os.path.join('assets', f'player_{i}.png')), (TILE_SIZE, TILE_SIZE)) for i in range(1, 4)
]
boost_symbol_image = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'boost_symbol.png')), (TILE_SIZE, TILE_SIZE))

class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    # Kreuz (X): Buchstaben einsammeln
    def on_x_press(self):
        global letters, player_pos
        for letter in letters[:]:
            if player_pos[0] == letter[0] and player_pos[1] == letter[1]:
                letters.remove(letter)
                print("Buchstabe eingesammelt!")

    # Kreis (O): Boost aktivieren
    def on_circle_press(self):
        global boost_active, boost_timer, player_speed
        if not boost_active:
            boost_active = True
            boost_timer = time.time()
            player_speed = boost_speed
            print("Boost aktiviert!")

    # Dreieck (∆): Schutzschild aktivieren
    def on_triangle_press(self):
        global shield_active, shield_timer
        if not shield_active:
            shield_active = True
            shield_timer = time.time()
            print("Schutzschild aktiviert!")

    # Quadrat (□): Anweisungen anzeigen
    def on_square_press(self):
        display_instructions()

    def on_L3_up(self, value):
        global player_pos, maze, player_speed
        if value < -10000 and player_pos[1] > 0 and maze[player_pos[1] - player_speed][player_pos[0]] == 0:
            player_pos[1] -= player_speed

    def on_L3_down(self, value):
        global player_pos, maze, player_speed
        if value > 10000 and player_pos[1] < MAZE_HEIGHT - 1 and maze[player_pos[1] + player_speed][player_pos[0]] == 0:
            player_pos[1] += player_speed

    def on_L3_left(self, value):
        global player_pos, maze, player_speed
        if value < -10000 and player_pos[0] > 0 and maze[player_pos[1]][player_pos[0] - player_speed] == 0:
            player_pos[0] -= player_speed

    def on_L3_right(self, value):
        global player_pos, maze, player_speed
        if value > 10000 and player_pos[0] < MAZE_WIDTH - 1 and maze[player_pos[1]][player_pos[0] + player_speed] == 0:
            player_pos[0] += player_speed

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller_thread = threading.Thread(target=controller.listen, daemon=True)
controller_thread.start()

# Auswahlmenü für Charaktere
def character_selection():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    instructions = [
        "Wähle deinen Charakter aus:",
        "1: Charakter 1",
        "2: Charakter 2",
        "3: Charakter 3"
    ]
    y_offset = 100
    for line in instructions:
        text = font.render(line, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 8, y_offset))
        y_offset += 50
    pygame.display.flip()
    waiting = True
    selected_character = None
    while waiting:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_1:
                    selected_character = 0
                    waiting = False
                elif event.key == K_2:
                    selected_character = 1
                    waiting = False
                elif event.key == K_3:
                    selected_character = 2
                    waiting = False
    return selected_character

player_image = player_images[character_selection()]

# Auswahlmenü für Bosse
def boss_selection():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    instructions = [
        "Wähle deinen Boss aus:",
        "1: Tom",
        "2: Jannik",
        "3: Phillip"
    ]
    y_offset = 100
    for line in instructions:
        text = font.render(line, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 8, y_offset))
        y_offset += 50
    pygame.display.flip()
    waiting = True
    selected_boss = None
    while waiting:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_1:
                    selected_boss = 0
                    waiting = False
                elif event.key == K_2:
                    selected_boss = 1
                    waiting = False
                elif event.key == K_3:
                    selected_boss = 2
                    waiting = False
    return selected_boss

selected_boss_index = boss_selection()

# Boss Bilder
boss_images = [
    pygame.transform.scale(pygame.image.load(os.path.join('assets', f'boss_{i}.png')), (TILE_SIZE, TILE_SIZE)) for i in range(1, 5)
]

# Fähigkeiten Bilder für jeden Boss
boss_abilities_images = [
    [
        pygame.transform.scale(pygame.image.load(os.path.join('assets', f'boss_{i}_ability_{j}.png')), (TILE_SIZE, TILE_SIZE)) for j in range(1, 3)  # Zwei Fähigkeiten pro Boss
    ] for i in range(1, 5)
]

# Eigenschaften der Bosse
boss_attributes = [
    {"name": "Tom", "ability": "teleport", "description": "Teleportiert sich und hinterlässt Rauch", "damage": 1, "speed": 1, "abilities": ["ability_1", "ability_2"]},
    {"name": "Jannik", "ability": "shoot_fibis", "description": "Schießt wütende Fibis", "damage": 1, "speed": 1.5, "abilities": ["ability_1", "ability_2"]},
    {"name": "Phillip", "ability": "long_range_attack", "description": "Besitzt eine große Angriffsreichweite", "damage": 2, "speed": 1.2, "abilities": ["ability_1", "ability_2"]},
    {"name": "Louis (Endboss)", "ability": "shoot_u_stahl", "description": "Schießt U-Stahl, der 3 Leben abzieht", "damage": 3, "speed": 2, "abilities": ["ability_1", "ability_2"]}
]

selected_boss = boss_attributes[selected_boss_index]
louis = boss_attributes[3]

# Position des gewählten Bosses
boss_positions = [[random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)]]
louis_spawned = False

# Boss KI für Verfolgung des Spielers
def boss_ai(player_pos, boss_pos, maze):
    # Verfolgt den Spieler durch eine einfache Wegfindungsstrategie
    boss_x, boss_y = boss_pos
    player_x, player_y = player_pos
    new_boss_x, new_boss_y = boss_x, boss_y

    # Priorität auf horizontale Bewegung, um den Spieler zu verfolgen
    if player_x > boss_x and maze[boss_y][boss_x + 1] == 0:
        new_boss_x += 1
    elif player_x < boss_x and maze[boss_y][boss_x - 1] == 0:
        new_boss_x -= 1
    # Falls horizontale Bewegung nicht möglich, vertikal bewegen
    elif player_y > boss_y and maze[boss_y + 1][boss_x] == 0:
        new_boss_y += 1
    elif player_y < boss_y and maze[boss_y - 1][boss_x] == 0:
        new_boss_y -= 1

    return [new_boss_x, new_boss_y]

# Anzeige der Anleitung vor Spielbeginn
def display_instructions():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    instructions = [
        "Willkommen im Labyrinth-Spiel!",
        "Verwende den PS4-Controller mit folgenden Tasten:",
        "Kreuz (X): Buchstaben einsammeln",
        "Kreis (O): Boost aktivieren",
        "Dreieck (∆): Schutzschild aktivieren",
        "Quadrat (□): Anweisungen anzeigen",
        "Sammle alle Buchstaben, um den Namen des Hauptsitzes von Weidmüller zu bilden.",
        "Vermeide die Bosse, die versuchen, dich aufzuhalten!",
        "Benutze den PS4-Controller, um dich zu bewegen.",
        "Du hast 3 Leben. Drücke einen beliebigen Knopf, um das Spiel zu starten."
    ]
    y_offset = 100
    for line in instructions:
        text = font.render(line, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 8, y_offset))
        y_offset += 50
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting = False

# Generiere das Labyrinth
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    stack = [(1, 1)]
    maze[1][1] = 0
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        current_cell = stack[-1]
        x, y = current_cell
        neighbors = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width-1 and 1 <= ny < height-1 and maze[ny][nx] == 1:
                neighbors.append((nx, ny))

        if neighbors:
            next_cell = random.choice(neighbors)
            stack.append(next_cell)
            maze[next_cell[1]][next_cell[0]] = 0
            maze[(y + next_cell[1]) // 2][(x + next_cell[0]) // 2] = 0
        else:
            stack.pop()

    return maze

maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
maze[player_pos[1]][player_pos[0]] = 0

letters = []
all_letters = list("HAUPTSITZVONWEIDMUELLER")
for letter in all_letters:
    while True:
        x = random.randint(1, MAZE_WIDTH - 2)
        y = random.randint(1, MAZE_HEIGHT - 2)
        if maze[y][x] == 0 and not any(l[0] == x and l[1] == y for l in letters):
            letters.append((x, y, letter))
            break

start_time = time.time()
timer_duration = 15 * 60

display_instructions()

running = True
while running:
    screen.fill(BLACK)

    elapsed_time = time.time() - start_time
    if elapsed_time >= timer_duration:
        print("Die Zeit ist abgelaufen! Du hast verloren.")
        time.sleep(3)
        player_pos = [1, 1]
        player_lives = 3
        letters = []
        for _ in range(20):
            while True:
                x = random.randint(1, MAZE_WIDTH - 2)
                y = random.randint(1, MAZE_HEIGHT - 2)
                if maze[y][x] == 0 and not any(l[0] == x and l[1] == y for l in letters):
                    letters.append((x, y, random.choice("HAUPTSITZVONWEIDMUELLER")))
                    break
        start_time = time.time()

    if not louis_spawned and elapsed_time >= timer_duration - 5 * 60:
        boss_positions.append([random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)])
        print("Der Endboss ist erschienen!")
        louis_spawned = True

    viewport_x = max(0, min(player_pos[0] - VIEWPORT_WIDTH // 2, MAZE_WIDTH - VIEWPORT_WIDTH))
    viewport_y = max(0, min(player_pos[1] - VIEWPORT_HEIGHT // 2, MAZE_HEIGHT - VIEWPORT_HEIGHT))

    for y in range(VIEWPORT_HEIGHT):
        for x in range(VIEWPORT_WIDTH):
            maze_x = viewport_x + x
            maze_y = viewport_y + y
            if maze_y < MAZE_HEIGHT and maze_x < MAZE_WIDTH and maze[maze_y][maze_x] == 1:
                pygame.draw.rect(screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    font = pygame.font.Font(None, 36)
    collected_letters = ''.join(sorted(set(char for _, _, char in letters if char not in "HAUPTSITZVONWEIDMUELLER")))
    collected_text = font.render(f"Gesammelt: {collected_letters}", True, GREEN)
    screen.blit(collected_text, (10, 70))
    collected_letters_count = {}
for letter in letters:
    x, y, char = letter
    color = CORRECT_LETTER_COLOR if char in "HAUPTSITZVONWEIDMUELLER" else WRONG_LETTER_COLOR
    if player_pos[0] == x and player_pos[1] == y:
        letters.remove(letter)
        print(f"Buchstabe {char} eingesammelt!")
        if char not in collected_letters_count:
            collected_letters_count[char] = 1
        else:
            collected_letters_count[char] += 1

        # Boost aktivieren, wenn der gleiche Buchstabe 3 Mal eingesammelt wurde
        if collected_letters_count[char] == 3:
            boost_active = True
            boost_timer = time.time()
            player_speed = boost_speed
            print(f"Boost aktiviert durch das Sammeln von 3x {char}!")
        if viewport_x <= x < viewport_x + VIEWPORT_WIDTH and viewport_y <= y < viewport_y + VIEWPORT_HEIGHT:
            screen_x = (x - viewport_x) * TILE_SIZE
            screen_y = (y - viewport_y) * TILE_SIZE
            text = font.render(char, True, color)
            screen.blit(text, (screen_x + TILE_SIZE // 4, screen_y + TILE_SIZE // 4))

    screen_x = (player_pos[0] - viewport_x) * TILE_SIZE
    screen_y = (player_pos[1] - viewport_y) * TILE_SIZE
    screen.blit(player_image, (screen_x, screen_y))

    if boost_active:
        screen.blit(boost_symbol_image, (screen_x, screen_y))  # Zeige leuchtendes Symbol über dem Spieler bei Boost

    for i, boss_pos in enumerate(boss_positions):
        if i < len(boss_positions) - 1:
            boss = selected_boss
        else:
            boss = louis
        boss_positions[i] = boss_ai(player_pos, boss_pos, maze)  # Boss KI verfolgt den Spieler
        boss_screen_x = (boss_positions[i][0] - viewport_x) * TILE_SIZE
        boss_screen_y = (boss_positions[i][1] - viewport_y) * TILE_SIZE
        screen.blit(boss_images[i], (boss_screen_x, boss_screen_y))

        if boss["ability"] == "teleport":
            if random.randint(0, 100) < 2:
                boss_positions[i] = [random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)]
                print(f"{boss['name']} hat sich teleportiert!")
                smoke_image = pygame.image.load(os.path.join('assets', 'smoke.gif'))
                smoke_image = pygame.transform.scale(smoke_image, (TILE_SIZE, TILE_SIZE))
                screen.blit(smoke_image, (boss_screen_x, boss_screen_y))
        elif boss["ability"] == "shoot_fibis":
            if random.randint(0, 100) < 3:
                fibis_image = pygame.image.load(os.path.join('assets', 'fibi.png'))
                fibis_image = pygame.transform.scale(fibis_image, (TILE_SIZE, TILE_SIZE))
                fibis_pos = boss_positions[i][:]
                if player_pos[0] > boss_positions[i][0]:
                    fibis_pos[0] += 1
                elif player_pos[0] < boss_positions[i][0]:
                    fibis_pos[0] -= 1
                if player_pos[1] > boss_positions[i][1]:
                    fibis_pos[1] += 1
                elif player_pos[1] < boss_positions[i][1]:
                    fibis_pos[1] -= 1
                screen.blit(fibis_image, (fibis_pos[0] * TILE_SIZE, fibis_pos[1] * TILE_SIZE))
                if player_pos == fibis_pos:
                    player_lives -= 1
                    print("Jannik's Fibi hat dich getroffen!")
        elif boss["ability"] == "long_range_attack":
            if abs(player_pos[0] - boss_positions[i][0]) <= 5 or abs(player_pos[1] - boss_positions[i][1]) <= 5:
                pygame.draw.line(screen, RED, (boss_screen_x + TILE_SIZE // 2, boss_screen_y + TILE_SIZE // 2), (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2), 2)
                if abs(player_pos[0] - boss_positions[i][0]) <= 1 and abs(player_pos[1] - boss_positions[i][1]) <= 1:
                    player_lives -= 1
                    print("Phillip hat dich aus großer Reichweite getroffen!")
        elif boss["ability"] == "shoot_u_stahl":
            if random.randint(0, 100) < 5:
                u_stahl_image = pygame.image.load(os.path.join('assets', 'u_stahl.png'))
                u_stahl_image = pygame.transform.scale(u_stahl_image, (TILE_SIZE, TILE_SIZE))
                u_stahl_pos = boss_positions[i][:]
                if player_pos[0] > boss_positions[i][0]:
                    u_stahl_pos[0] += 1
                elif player_pos[0] < boss_positions[i][0]:
                    u_stahl_pos[0] -= 1
                if player_pos[1] > boss_positions[i][1]:
                    u_stahl_pos[1] += 1
                elif player_pos[1] < boss_positions[i][1]:
                    u_stahl_pos[1] -= 1
                screen.blit(u_stahl_image, (u_stahl_pos[0] * TILE_SIZE, u_stahl_pos[1] * TILE_SIZE))
                if player_pos == u_stahl_pos:
                    player_lives -= 3
                    print("Louis' U-Stahl hat dich getroffen! 3 Leben abgezogen!")

    lives_text = font.render(f"Leben: {player_lives}", True, GREEN)
    screen.blit(lives_text, (10, 10))

    if shield_active:
        shield_time_left = shield_duration - (time.time() - shield_timer)
        if shield_time_left <= 0:
            shield_active = False
            shield_timer = time.time()
        shield_text = font.render(f"Schutzschild: {shield_symbol} ({int(shield_time_left)}s)", True, GREEN)
    else:
        cooldown_time_left = shield_cooldown - (time.time() - shield_timer)
        if cooldown_time_left <= 0:
            shield_active = True
            shield_timer = time.time()
            cooldown_time_left = shield_cooldown
        shield_text = font.render(f"Schutzschild bereit in: {int(cooldown_time_left)}s", True, RED)
    screen.blit(shield_text, (10, 40))

    if boost_active:
        boost_time_left = boost_duration - (time.time() - boost_timer)
        if boost_time_left <= 0:
            boost_active = False
            player_speed = normal_speed
            print("Boost deaktiviert!")

    if player_lives <= 0:
        print("Du wurdest vom Boss erwischt! Spiel vorbei.")
        time.sleep(3)
        player_pos = [1, 1]
        player_lives = 3
        letters = []
        for _ in range(20):
            while True:
                x = random.randint(1, MAZE_WIDTH - 2)
                y = random.randint(1, MAZE_HEIGHT - 2)
                if maze[y][x] == 0 and not any(l[0] == x and l[1] == y for l in letters):
                    letters.append((x, y, random.choice("WEIDMUELLER")))
                    break
        start_time = time.time()
        screen.fill(BLACK)
        end_text = font.render("Du wurdest vom Boss erwischt!", True, RED)
        screen.blit(end_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        time.sleep(5)
        continue

        print("Glückwunsch! Du hast alle Buchstaben gesammelt und das Spiel gewonnen!")
        collected_text = font.render(f"Du hast gesammelt: Hauptsitz von Weidmüller", True, GREEN)
        screen.blit(collected_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(35)
        screen.fill(BLACK)
        credits_text = font.render("Developer: Jannik, Tom", True, WHITE)
        screen.blit(credits_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 60))
        design_text = font.render("Design: Louis, Jannik", True, WHITE)
        screen.blit(design_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        ideas_text = font.render("Ideen: Phillip, Cora, Jannes, Chris, Laurin", True, WHITE)
        screen.blit(ideas_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 60))
        pygame.display.flip()
        time.sleep(10)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
controller.stop()
