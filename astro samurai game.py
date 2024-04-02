import pygame
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Set up the screen
WIDTH, HEIGHT = 720, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Astro Samurai")

# Load background image
background = pygame.image.load('bg.png').convert()

# Load player idle sprite
player_idle_sheet = pygame.image.load('idle.png').convert_alpha()

# Load player shooting sprite
player_shooting_sheet = pygame.image.load('bladeshot.png').convert_alpha()

# Load enemy meteor sprite
meteor_sheet = pygame.image.load('meteor.png').convert_alpha()

# Load alien sprite sheet
alien_sheet = pygame.image.load('alien.png').convert_alpha()
alien_width, alien_height = 64, 64

# Load rip image for game over screen
rip_image = pygame.image.load('rip.png').convert_alpha()
rip_width, rip_height = 64, 64

# Load health image
health_image = pygame.image.load('health3.png').convert_alpha()
health_width, health_height = 32, 32

# Load music
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1)  # Play the music on loop

# Load shooting sound
shooting_sound = pygame.mixer.Sound('pew1.mp3')

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Define rectangle properties
player_width, player_height = 32, 32
player_x, player_y = 50, HEIGHT // 2 - player_height // 2
player_speed = 5

# Speed power-up variables
speed_powerup_duration = 10  # Duration of speed power-up in seconds
speed_powerup_multiplier = 1.5  # Increase in player speed during power-up
speed_powerup_timer = 0  # Timer for the speed power-up effect

# Shooting variables
last_shooting_time = 0  # Time when last bullet was fired
shooting_delay = 200  # Delay between each shot in milliseconds

# Timer variables
timer_font = pygame.font.Font(None, 36)
start_time = pygame.time.get_ticks()
time_alive = 0

# Sprite animation variables
current_frame = 0  # Initialize current frame for player animation
frame_count = 6  # 6 frames for the shooting animation
animation_speed = 150  # Adjust animation speed as needed
last_update = pygame.time.get_ticks()

# Enemy meteor variables
meteor_speed = 7

# Yellow circle variables
yellow_circle_radius = 16
yellow_circle_speed = 3
last_yellow_circle_spawn = pygame.time.get_ticks()

# Purple square variables
purple_square_width, purple_square_height = 15, 15
purple_square_speed = 15  # Adjust bullet speed as needed
purple_squares = []

# Alien variables
alien_speed = 2
alien_spawn_delay = 8000  # Spawn delay for aliens in milliseconds
last_alien_spawn = pygame.time.get_ticks()
aliens = []  # List to store alien positions

# Sprite animation variables
alien_current_frame = 0  # Initialize current frame for alien animation
alien_frame_count = 6  # 6 frames for the alien animation
alien_animation_speed = 150  # Adjust animation speed as needed
alien_last_update = pygame.time.get_ticks()  # Initialize last update time for alien animation

# Dictionary to store collision count for each alien
alien_collision_count = {}

# Function to draw enemy meteor
def draw_meteor(x, y):
    screen.blit(meteor_sheet, (x, y), (current_frame * player_width, 0, player_width, player_height))

# Function to draw yellow circle
def draw_yellow_circle(x, y):
    pygame.draw.circle(screen, YELLOW, (x, y), yellow_circle_radius)

# Function to draw purple squares
def draw_purple_squares():
    for square in purple_squares:
        pygame.draw.rect(screen, PURPLE, square)

# Function to draw aliens
def draw_aliens():
    for alien in aliens:
        screen.blit(alien_sheet, (alien[0], alien[1]), (alien_current_frame * alien_width, 0, alien_width, alien_height))

# Function to display game over screen with timer
def game_over():
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 100)
    text = font.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(text, text_rect)
    rip_rect = rip_image.get_rect(center=(WIDTH // 2, rip_height // 2 + 100))
    screen.blit(rip_image, rip_rect)
    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
    pygame.draw.rect(screen, RED, restart_button)
    font = pygame.font.Font(None, 36)
    text = font.render("Restart", True, WHITE)
    text_rect = text.get_rect(center=restart_button.center)
    screen.blit(text, text_rect)
    pygame.display.flip()
    # Wait for user input to restart
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(pygame.mouse.get_pos()):
                return True

# Main game loop
running = True
clock = pygame.time.Clock()

enemies = []  # List to store enemy rectangles
yellow_circles = []  # List to store yellow circle positions

# Initial position for background scrolling
bg_x = 0

# Flag for shooting animation
shooting = False
shooting_duration = 0.2  # Duration of shooting animation in seconds
shooting_start_time = 0  # Time when shooting animation started

# Flag for shooting sound
shooting_sound_playing = False

# Player health
player_health = 3

while running:
    screen.fill((0, 0, 0))  # Fill screen with black color

    # Draw background image
    screen.blit(background, (bg_x, 0))
    screen.blit(background, (bg_x + background.get_width(), 0))

    # Scroll background infinitely to the left
    bg_x -= 1
    if bg_x <= -background.get_width():
        bg_x = 0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shooting_sound.play()  # Start playing shooting sound
                shooting = True
                shooting_start_time = pygame.time.get_ticks()  # Record the time when shooting animation starts
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                shooting_sound.stop()  # Stop playing shooting sound
                shooting = False

    # Player sprite animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update > animation_speed:
        current_frame = (current_frame + 1) % frame_count
        last_update = current_time

    # Draw player sprite
    if shooting:
        player_rect = pygame.Rect(current_frame * player_width, 0, player_width, player_height)
        screen.blit(player_shooting_sheet, (player_x, player_y), player_rect)
    else:
        player_rect = pygame.Rect(current_frame * player_width, 0, player_width, player_height)
        screen.blit(player_idle_sheet, (player_x, player_y), player_rect)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed
    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed

    # Ensure player stays within the screen boundaries
    player_x = max(0, min(player_x, WIDTH - player_width))
    player_y = max(0, min(player_y, HEIGHT - player_height))

    # Generate and draw enemies (meteors)
    if random.randint(0, 100) < 5:  # Adjust the probability to control enemy spawning rate
        enemy_y = random.randint(0, HEIGHT - player_height)
        enemies.append([WIDTH, enemy_y])

    for enemy in enemies[:]:
        enemy[0] -= meteor_speed
        draw_meteor(enemy[0], enemy[1])
        if enemy[0] < player_x + player_width and enemy[0] + player_width > player_x and \
           enemy[1] < player_y + player_height and enemy[1] + player_height > player_y:
            # Decrease player health if enemy collides with player
            player_health -= 1
            if player_health <= 0:
                # Game over if player health reaches zero
                game_over()
                # Reset player position and remove enemies
                player_x, player_y = 50, HEIGHT // 2 - player_height // 2
                enemies.clear()
                # Reset timer
                start_time = pygame.time.get_ticks()
                time_alive = 0
                # Reset player health
                player_health = 3
            else:
                # Reset player position if not game over
                player_x, player_y = 50, HEIGHT // 2 - player_height // 2
                # Remove the collided enemy
                enemies.remove(enemy)

    # Remove enemy if it goes off the left side of the screen
    for enemy in enemies[:]:
        if enemy[0] < -player_width:
            enemies.remove(enemy)

    # Generate and draw yellow circles
    if current_time - last_yellow_circle_spawn >= 30000:  # Spawn every 30 seconds
        yellow_circle_y = random.randint(0, HEIGHT - yellow_circle_radius * 2)
        yellow_circles.append([0, yellow_circle_y])
        last_yellow_circle_spawn = current_time

    for yellow_circle in yellow_circles[:]:
        yellow_circle[0] += yellow_circle_speed
        draw_yellow_circle(yellow_circle[0], yellow_circle[1])

        # Collision detection with player
        if (player_x - yellow_circle_radius < yellow_circle[0] < player_x + player_width and
                player_y - yellow_circle_radius < yellow_circle[1] < player_y + player_height):
            # Increase player speed by 50% for 10 seconds
            player_speed *= 1.5
            speed_powerup_timer = pygame.time.get_ticks()
            yellow_circles.remove(yellow_circle)

        # Remove yellow circle if it goes off the right side of the screen
        if yellow_circle[0] > WIDTH:
            yellow_circles.remove(yellow_circle)

    # Handle speed power-up duration
    if speed_powerup_timer != 0 and current_time - speed_powerup_timer >= speed_powerup_duration * 1000:
        player_speed /= 1.5  # Reset player speed back to normal
        speed_powerup_timer = 0  # Reset timer

    # Update timer
    time_alive = current_time - start_time

    # Player shooting mechanic
    if keys[pygame.K_SPACE] and current_time - last_shooting_time >= shooting_delay:
        shooting = True
        shooting_start_time = current_time  # Record the time when shooting animation starts
        shooting_sound.play()  # Start playing shooting sound
        # Create a new purple square at the player's position
        purple_square_x = player_x + player_width
        purple_square_y = player_y + player_height // 2 - purple_square_height // 2
        purple_squares.append(pygame.Rect(purple_square_x, purple_square_y, purple_square_width, purple_square_height))
        last_shooting_time = current_time

    # Move and draw purple squares
    for square in purple_squares[:]:
        square.x += purple_square_speed
        pygame.draw.rect(screen, PURPLE, square)

        # Remove purple square if it goes off the right side of the screen
        if square.x > WIDTH:
            purple_squares.remove(square)

        # Collision detection with aliens
        for i, alien in enumerate(aliens):
            if square.colliderect(pygame.Rect(alien[0], alien[1], alien_width, alien_height)):
                # Increase collision count for the alien
                if i in alien_collision_count:
                    alien_collision_count[i] += 1
                else:
                    alien_collision_count[i] = 1
                # If collision count reaches 10, remove the alien
                if alien_collision_count[i] >= 10:
                    aliens.remove(alien)
                    alien_collision_count.pop(i)
                # Remove the purple square
                purple_squares.remove(square)
                break

    # Check if shooting animation duration has elapsed
    if shooting and current_time - shooting_start_time >= shooting_duration * 1000:
        shooting = False  # Reset the shooting flag after the duration has elapsed
        shooting_sound.stop()  # Stop playing shooting sound

    # Draw player sprite based on shooting flag
    if shooting:
        player_rect = pygame.Rect(current_frame * player_width, 0, player_width, player_height)
        screen.blit(player_shooting_sheet, (player_x, player_y), player_rect)
    else:
        player_rect = pygame.Rect(current_frame * player_width, 0, player_width, player_height)
        screen.blit(player_idle_sheet, (player_x, player_y), player_rect)

    # Display timer in top-right corner
    timer_text = timer_font.render(f"{time_alive // 60000:02}:{(time_alive // 1000) % 60:02}", True, WHITE)
    timer_rect = timer_text.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(timer_text, timer_rect)

    # Display health
    for i in range(player_health):
        screen.blit(health_image, (10 + i * (health_width + 5), 10))

    # Spawn aliens
    if current_time - last_alien_spawn >= alien_spawn_delay:
        alien_y = random.randint(0, HEIGHT - alien_height)
        aliens.append([WIDTH, alien_y])
        last_alien_spawn = current_time

    # Move and draw aliens
    for alien in aliens[:]:
        alien[0] -= alien_speed
        screen.blit(alien_sheet, (alien[0], alien[1]), (alien_current_frame * alien_width, 0, alien_width, alien_height))

        # Remove alien if it goes off the left side of the screen
        if alien[0] < -alien_width:
            aliens.remove(alien)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
