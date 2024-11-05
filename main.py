import pygame
import random
import RPi.GPIO as GPIO
import time
from pygame.locals import *

TILE_SIZE = 40
MAZE_WIDTH = 15
MAZE_HEIGHT = 10
VIEWPORT_WIDTH = 10
VIEWPORT_HEIGHT = 6
SCREEN_WIDTH = TILE_SIZE * VIEWPORT_WIDTH
SCREEN_HEIGHT = TILE_SIZE * VIEWPORT_HEIGHT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

player_pos = [1, 1]

GPIO.setmode(GPIO.BCM)
UP_PIN = 17
DOWN_PIN = 18
LEFT_PIN = 27
RIGHT_PIN = 22

GPIO.setup(UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Labyrinth with Letters')
clock = pygame.time.Clock()

player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))

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

word = "WEITMÜLLER"
letters = []
for char in word:
    while True:
        x = random.randint(1, MAZE_WIDTH - 2)
        y = random.randint(1, MAZE_HEIGHT - 2)
        if maze[y][x] == 0 and not any(l[0] == x and l[1] == y for l in letters):
            letters.append((x, y, char))
            break

start_time = time.time()
timer_duration = 10 * 60

running = True
while running:
    screen.fill(WHITE)

    elapsed_time = time.time() - start_time
    if elapsed_time >= timer_duration:
        running = False
        print("Time's up! You ran out of time.")

    viewport_x = max(0, min(player_pos[0] - VIEWPORT_WIDTH // 2, MAZE_WIDTH - VIEWPORT_WIDTH))
    viewport_y = max(0, min(player_pos[1] - VIEWPORT_HEIGHT // 2, MAZE_HEIGHT - VIEWPORT_HEIGHT))

    for y in range(VIEWPORT_HEIGHT):
        for x in range(VIEWPORT_WIDTH):
            maze_x = viewport_x + x
            maze_y = viewport_y + y
            if maze_y < MAZE_HEIGHT and maze_x < MAZE_WIDTH and maze[maze_y][maze_x] == 1:
                pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    font = pygame.font.Font(None, 36)
    for letter in letters:
        x, y, char = letter
        if viewport_x <= x < viewport_x + VIEWPORT_WIDTH and viewport_y <= y < viewport_y + VIEWPORT_HEIGHT:
            screen_x = (x - viewport_x) * TILE_SIZE
            screen_y = (y - viewport_y) * TILE_SIZE
            text = font.render(char, True, BLACK)
            screen.blit(text, (screen_x + TILE_SIZE // 4, screen_y + TILE_SIZE // 4))

    screen_x = (player_pos[0] - viewport_x) * TILE_SIZE
    screen_y = (player_pos[1] - viewport_y) * TILE_SIZE
    screen.blit(player_image, (screen_x, screen_y))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    new_x, new_y = player_pos
    if GPIO.input(UP_PIN) == GPIO.HIGH and new_y > 0 and maze[new_y - 1][new_x] == 0:
        new_y -= 1
    elif GPIO.input(DOWN_PIN) == GPIO.HIGH and new_y < MAZE_HEIGHT - 1 and maze[new_y + 1][new_x] == 0:
        new_y += 1
    elif GPIO.input(LEFT_PIN) == GPIO.HIGH and new_x > 0 and maze[new_y][new_x - 1] == 0:
        new_x -= 1
    elif GPIO.input(RIGHT_PIN) == GPIO.HIGH and new_x < MAZE_WIDTH - 1 and maze[new_y][new_x + 1] == 0:
        new_x += 1
    player_pos = [new_x, new_y]

    for letter in letters[:]:
        if player_pos[0] == letter[0] and player_pos[1] == letter[1]:
            letters.remove(letter)

    if not letters:
        running = False
        print("Congratulations! You collected all the letters and won the game!")
        screen.fill(WHITE)
        end_text = font.render(f"You collected: {word}", True, BLACK)
        screen.blit(end_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        time.sleep(5)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
GPIO.cleanup()
