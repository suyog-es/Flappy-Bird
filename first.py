import pygame
import random
import sqlite3
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Game variables
gravity = 0.5
bird_movement = 0
game_active = False
score = 0
high_score = 0

# Load images
bird_surface = pygame.image.load("bird.png").convert_alpha()
bird_surface = pygame.transform.scale(bird_surface, (40, 30))
bird_rect = bird_surface.get_rect(center=(100, HEIGHT // 2))

pipe_surface = pygame.image.load("pipe.png").convert_alpha()
pipe_list = []

# Timer for spawning pipes
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

# Font
game_font = pygame.font.Font(None, 40)

# Power-up variables
power_up_active = False
power_up_timer = 0
POWER_UP_DURATION = 5000  # 5 seconds

# Database setup
conn = sqlite3.connect("flappy_bird.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS high_scores
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   score INTEGER,
                   date TEXT)''')
conn.commit()

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 550))
    screen.blit(floor_surface, (floor_x_pos + WIDTH, 550))

def create_pipe():
    random_pipe_pos = random.choice([300, 350, 400, 450])
    bottom_pipe = pipe_surface.get_rect(midtop=(WIDTH + 100, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(WIDTH + 100, random_pipe_pos - 200))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 550:
        return False
    return True

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect

def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, WHITE)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, 500))
        screen.blit(high_score_surface, high_score_rect)

def update_score(score):
    global high_score
    if score > high_score:
        high_score = score
        cursor.execute("INSERT INTO high_scores (score, date) VALUES (?, datetime('now'))", (score,))
        conn.commit()

def activate_power_up():
    global power_up_active, power_up_timer
    power_up_active = True
    power_up_timer = pygame.time.get_ticks()

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -10
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, HEIGHT // 2)
                bird_movement = 0
                score = 0
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

    screen.fill(BLACK)

    if game_active:
        # Bird movement
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)

        # Pipes movement
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Check collisions
        game_active = check_collision(pipe_list)

        # Update and display score
        score += 0.01
        score_display('main_game')

        # Power-up logic
        if power_up_active:
            current_time = pygame.time.get_ticks()
            if current_time - power_up_timer >= POWER_UP_DURATION:
                power_up_active = False
            else:
                # Draw power-up effect (e.g., a glowing aura around the bird)
                pygame.draw.circle(screen, (255, 255, 0), bird_rect.center, 30, 2)

        # Randomly activate power-up
        if random.randint(1, 1000) == 1 and not power_up_active:
            activate_power_up()

    else:
        update_score(int(score))
        score_display('game_over')

    # Floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -WIDTH:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(60)

# Close the database connection
conn.close()

# Quit Pygame
pygame.quit()