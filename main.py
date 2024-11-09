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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Labyrinth with Letters (Raspberry Pi Touchscreen Edition)')
clock = pygame.time.Clock()

player_images = [
    pygame.transform.scale(pygame.image.load(os.path.join('assets', f'player_{i}.png')), (TILE_SIZE, TILE_SIZE)) for i in range(1, 4)
]

class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    def on_x_press(self):
        Game.collect_letter()

    def on_circle_press(self):
        Game.activate_boost()

    def on_triangle_press(self):
        Game.activate_shield()

    def on_square_press(self):
        Game.display_instructions()

    def on_L3_up(self, value):
        if value < -10000:
            Game.player.move(0, -1)

    def on_L3_down(self, value):
        if value > 10000:
            Game.player.move(0, 1)

    def on_L3_left(self, value):
        if value < -10000:
            Game.player.move(-1, 0)

    def on_L3_right(self, value):
        if value > 10000:
            Game.player.move(1, 0)

class Player:
    def __init__(self, image, pos):
        self.image = image
        self.pos = pos
        self.lives = 3
        self.shield_active = False
        self.shield_timer = 0
        self.boost_active = False
        self.boost_timer = 0

    def move(self, dx, dy):
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and Game.maze[new_y][new_x] == 0:
            self.pos[0] = new_x
            self.pos[1] = new_y

    def draw(self, screen):
        screen_x = (self.pos[0] - Game.viewport_x) * TILE_SIZE
        screen_y = (self.pos[1] - Game.viewport_y) * TILE_SIZE
        if self.shield_active:
            pygame.draw.circle(screen, BLUE, (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2), TILE_SIZE // 2 + 5, 3)
        if self.boost_active:
            pygame.draw.line(screen, YELLOW, (screen_x, screen_y + TILE_SIZE), (screen_x + TILE_SIZE, screen_y), 5)
        screen.blit(self.image, (screen_x, screen_y))

class Boss:
    def __init__(self, name, image, pos, ability):
        self.name = name
        self.image = image
        self.pos = pos
        self.ability = ability
        self.move_counter = 0

    def move_towards_player(self, player_pos):
        if self.move_counter % 10 == 0:
            if abs(player_pos[0] - self.pos[0]) > abs(player_pos[1] - self.pos[1]):
                if Game.maze[self.pos[1]][self.pos[0] + (1 if player_pos[0] > self.pos[0] else -1)] == 0:
                    self.pos[0] += 1 if player_pos[0] > self.pos[0] else -1
            else:
                if Game.maze[self.pos[1] + (1 if player_pos[1] > self.pos[1] else -1)][self.pos[0]] == 0:
                    self.pos[1] += 1 if player_pos[1] > self.pos[1] else -1
        self.move_counter += 1

    def draw(self, screen):
        screen_x = (self.pos[0] - Game.viewport_x) * TILE_SIZE
        screen_y = (self.pos[1] - Game.viewport_y) * TILE_SIZE
        screen.blit(self.image, (screen_x, screen_y))

class Game:
    player = None
    bosses = []
    letters = []
    maze = []
    viewport_x = 0
    viewport_y = 0

    @staticmethod
    def init():
        Game.maze = Game.generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        Game.player = Player(player_images[Game.character_selection()], [1, 1])
        Game.bosses.append(Boss("Jannik", pygame.image.load(os.path.join('assets', 'boss_1.png')), [10, 10], "shoot_fibis"))
        Game.generate_letters()
        Game.display_instructions()

    @staticmethod
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

    @staticmethod
    def generate_letters():
        Game.letters = []
        for _ in range(20):
            while True:
                x = random.randint(1, MAZE_WIDTH - 2)
                y = random.randint(1, MAZE_HEIGHT - 2)
                if Game.maze[y][x] == 0 and not any(l[0] == x and l[1] == y for l in Game.letters):
                    Game.letters.append((x, y, random.choice("WEIDMUELLER")))
                    break

    @staticmethod
    def character_selection():
        return 0

    @staticmethod
    def display_instructions():
        pass

    @staticmethod
    def collect_letter():
        for letter in Game.letters[:]:
            if Game.player.pos[0] == letter[0] and Game.player.pos[1] == letter[1]:
                Game.letters.remove(letter)
                print("Buchstabe eingesammelt!")

    @staticmethod
    def activate_boost():
        if not Game.player.boost_active:
            Game.player.boost_active = True
            Game.player.boost_timer = time.time()
            print("Boost aktiviert!")

    @staticmethod
    def activate_shield():
        if not Game.player.shield_active:
            Game.player.shield_active = True
            Game.player.shield_timer = time.time()
            print("Schutzschild aktiviert!")

    @staticmethod
    def update():
        Game.viewport_x = max(0, min(Game.player.pos[0] - VIEWPORT_WIDTH // 2, MAZE_WIDTH - VIEWPORT_WIDTH))
        Game.viewport_y = max(0, min(Game.player.pos[1] - VIEWPORT_HEIGHT // 2, MAZE_HEIGHT - VIEWPORT_HEIGHT))
        for boss in Game.bosses:
            boss.move_towards_player(Game.player.pos)

        if Game.player.boost_active and time.time() - Game.player.boost_timer > 5:
            Game.player.boost_active = False
        if Game.player.shield_active and time.time() - Game.player.shield_timer > 5:
            Game.player.shield_active = False

    @staticmethod
    def draw():
        screen.fill(BLACK)
        for y in range(VIEWPORT_HEIGHT):
            for x in range(VIEWPORT_WIDTH):
                maze_x = Game.viewport_x + x
                maze_y = Game.viewport_y + y
                if maze_y < MAZE_HEIGHT and maze_x < MAZE_WIDTH and Game.maze[maze_y][maze_x] == 1:
                    pygame.draw.rect(screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        Game.player.draw(screen)
        for boss in Game.bosses:
            boss.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    Game.init()
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller_thread = controller.start()
    running = True
    while running:
        try:
            Game.update()
            Game.draw()
            clock.tick(30)
        except Exception as e:
            print(f"Fehler: {e}")
            running = False
    pygame.quit()
    controller.stop()
