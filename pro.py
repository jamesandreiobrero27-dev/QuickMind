import pygame
import sys
import time
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("QUICK MIND")

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 100, 200)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
RED = (200, 0, 0)
YELLOW = (255, 200, 0)

# Fonts
font = pygame.font.SysFont("Arial", 24)
button_font = pygame.font.SysFont("Arial", 36)

# Player setup
player_size = 60
player_x = WIDTH // 2
player_y = HEIGHT - player_size
player_vel_y = 0
player_speed = 10
gravity = 0.8
jump_strength = -20
on_ground = True

clock = pygame.time.Clock()

# Game states
STATE_NAME_INPUT = "name_input"
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
current_state = STATE_NAME_INPUT

# Player info
player_name = ""
score = 0
hp = 3
max_hp = 10

# Timer
start_time = None

# Math problem
math_problem = ""
math_answer = 0
user_answer = ""
last_math_time = 0
math_interval = 10  # seconds to answer

# Falling blocks
blocks = []
spawn_interval = 0.75
last_spawn_time = 0

def generate_math_problem():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(["+", "-", "*"])
    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    else:
        result = a * b
    return f"{a} {op} {b} = ?", result

def draw_button(text, x, y, width, height, color=GRAY):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def handle_button_click(event, rect):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if rect.collidepoint(event.pos):
            return True
    return False

def draw_name_input():
    screen.fill(WHITE)
    prompt = font.render("Enter your name:", True, BLACK)
    name_text = font.render(player_name, True, BLUE)
    screen.blit(prompt, (WIDTH//2 - 100, HEIGHT//2 - 40))
    screen.blit(name_text, (WIDTH//2 - 100, HEIGHT//2))
    pygame.display.flip()

def draw_start_screen():
    screen.fill(WHITE)
    button_text = button_font.render("Start Game", True, BLACK)
    button_rect = button_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    pygame.draw.rect(screen, GRAY, button_rect.inflate(30, 10))
    screen.blit(button_text, button_rect)
    pygame.display.flip()
    return button_rect

def draw_game_screen():
    elapsed_time = int(time.time() - start_time)
    timer_text = font.render(f"Time: {elapsed_time}s", True, BLACK)
    name_text = font.render(f"Player: {player_name}", True, BLACK)
    score_text = font.render(f"Score: {score}", True, BLACK)
    hp_text = font.render(f"HP: {hp}/{max_hp}", True, RED)

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 10, WIDTH, 10))
    screen.blit(timer_text, (10, 10))
    screen.blit(name_text, (10, 40))
    screen.blit(score_text, (10, 70))
    screen.blit(hp_text, (10, 100))

    # Draw math problem
    if math_problem:
        math_text = font.render(math_problem, True, BLACK)
        screen.blit(math_text, (WIDTH//2 - 50, 50))
        # Countdown
        time_left = max(0, math_interval - int(time.time() - last_math_time))
        countdown_text = font.render(f"Answer in: {time_left}s", True, RED if time_left <= 3 else BLACK)
        screen.blit(countdown_text, (WIDTH//2 - 70, 110))
        # User answer
        if user_answer:
            answer_text = font.render(user_answer, True, BLUE)
            screen.blit(answer_text, (WIDTH//2 - 50, 80))

    # Draw falling blocks
    for bx, by, width, height, speed, color, effect in blocks:
        pygame.draw.rect(screen, color, (bx, by, width, height))

    pygame.display.flip()

def draw_game_over():
    screen.fill(WHITE)
    over_text = button_font.render("GAME OVER", True, RED)
    final_score = score + hp
    score_text = font.render(f"Final Score: {final_score}", True, BLACK)
    name_text = font.render(f"Name: {player_name}", True, BLACK)
    screen.blit(over_text, (WIDTH // 3 - 100, HEIGHT // 3 - 40))
    screen.blit(score_text, (WIDTH // 3 - 100, HEIGHT // 3 - 10))
    screen.blit(name_text, (WIDTH // 3 - 80, HEIGHT // 3 + 10))
    retry_rect = draw_button("Retry", WIDTH // 3 - 75, HEIGHT // 3 + 50, 150, 50)
    quit_rect = draw_button("Quit", WIDTH // 3 + 75, HEIGHT // 3 + 50, 150, 50)
    pygame.display.flip()
    return retry_rect, quit_rect

# Initialize first math problem
math_problem, math_answer = generate_math_problem()

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle input based on state
        if current_state == STATE_NAME_INPUT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip() != "":
                    current_state = STATE_START
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if event.unicode.isprintable():
                        player_name += event.unicode
        elif current_state == STATE_START:
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_button_rect = draw_start_screen()
                if start_button_rect.collidepoint(event.pos):
                    # Start game
                    current_state = STATE_PLAYING
                    start_time = time.time()
                    # Reset variables
                    score = 0
                    hp = 3
                    player_x = WIDTH // 2
                    player_y = HEIGHT - player_size
                    user_answer = ""
                    blocks.clear()
                    math_problem, math_answer = generate_math_problem()
                    last_math_time = time.time()
        elif current_state == STATE_PLAYING:
            # Math input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_answer.strip() != "":
                        try:
                            if int(user_answer) == math_answer:
                                score += 100
                            else:
                                hp -= 1
                        except:
                            pass
                        user_answer = ""
                        math_problem, math_answer = generate_math_problem()
                        last_math_time = time.time()
                elif event.key == pygame.K_BACKSPACE:
                    user_answer = user_answer[:-1]
                else:
                    if event.unicode.isdigit():
                        user_answer += event.unicode
        elif current_state == STATE_GAME_OVER:
            # Buttons handled after drawing
            pass

    # State-specific updates
    if current_state == STATE_NAME_INPUT:
        draw_name_input()
        continue
    elif current_state == STATE_START:
        draw_start_screen()
        continue
    elif current_state == STATE_GAME_OVER:
        retry_rect, quit_rect = draw_game_over()
        # Handle button clicks
        for event in pygame.event.get():
            if handle_button_click(event, retry_rect):
                # Restart game
                current_state = STATE_START
            elif handle_button_click(event, quit_rect):
                pygame.quit()
                sys.exit()
        continue

    # Main game logic
    if current_state == STATE_PLAYING:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = jump_strength
            on_ground = False

        # Gravity
        player_vel_y += gravity
        player_y += player_vel_y

        # Ground collision
        if player_y >= HEIGHT - player_size:
            player_y = HEIGHT - player_size
            player_vel_y = 0
            on_ground = True

        # Bounds
        player_x = max(0, min(WIDTH - player_size, player_x))

        # Math timeout penalty
        if time.time() - last_math_time > math_interval:
            if user_answer.strip() == "":
                hp -= 2
            user_answer = ""
            math_problem, math_answer = generate_math_problem()
            last_math_time = time.time()

        # Spawn falling blocks
        if time.time() - last_spawn_time > spawn_interval:
            size = random.randint(10, 60)
            speed = random.randint(5, 11)
            effect = random.choice(["damage", "heal", "bonus"])
            if effect == "damage":
                color = RED
                width = size * 5
                height = size
            elif effect == "heal":
                color = GREEN
                width = size * 2
                height = size
            else:
                color = YELLOW
                width = size * 3
                height = size
            bx = random.randint(0, WIDTH - width)
            blocks.append([bx, 0, width, height, speed, color, effect])
            last_spawn_time = time.time()

        # Move blocks and check collision
        new_blocks = []
        for bx, by, width, height, speed, color, effect in blocks:
            by += speed
            if by < HEIGHT:
                new_blocks.append([bx, by, width, height, speed, color, effect])
            # Collision detection
            if (player_x < bx + width and
                player_x + player_size > bx and
                player_y < by + height and
                player_y + player_size > by):
                if effect == "damage":
                    hp -= 0.5
                elif effect == "heal":
                    hp = min(max_hp, hp + 1)
                elif effect == "bonus":
                    score += 20
        blocks = new_blocks

        # Check game over
        if hp <= 0:
            current_state = STATE_GAME_OVER

        # Draw everything
        draw_game_screen()

    clock.tick(60)