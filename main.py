import pygame
import random
import time
from moviepy.editor import ImageSequenceClip
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Ping Pong Game')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (36, 36, 64)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
PLAYER_COLOR = (0, 255, 0)  # Green
AI_COLOR = (255, 0, 0)      # Red
FIRE_COLORS = [(255, 69, 0), (255, 140, 0)]  # Red-orange, Dark orange

# Fonts
font = pygame.font.Font(None, 74)
menu_font = pygame.font.Font(None, 50)
log_font = pygame.font.Font(None, 30)
timer_font = pygame.font.Font(None, 40)

# Ball trail storage
ball_trail = []
game_logs = []

# Load sound effects
hit_sound = pygame.mixer.Sound('hit.wav')
score_sound = pygame.mixer.Sound('score.mp3')
pause_sound = pygame.mixer.Sound('pause.wav')

# Pause state
paused = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = random.randint(10, 20)
        self.size = random.randint(2, 5)
        self.velocity_x = random.uniform(-1, 1)
        self.velocity_y = random.uniform(-1, 1)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = max(0, int(255 * (self.lifetime / 20)))
            particle_color = (*self.color, alpha)
            particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (self.size // 2, self.size // 2), self.size // 2)
            surface.blit(particle_surface, (self.x, self.y))

class Paddle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 20, 100)
        self.speed = 10
        self.target_y = y
        self.color = color

    def move(self, direction):
        if direction == "up" and self.rect.top > 0:
            self.target_y -= self.speed
        elif direction == "down" and self.rect.bottom < SCREEN_HEIGHT:
            self.target_y += self.speed

    def update(self):
        # Smooth movement to target position
        if self.rect.centery < self.target_y:
            self.rect.y += min(self.speed, self.target_y - self.rect.centery)
        elif self.rect.centery > self.target_y:
            self.rect.y -= min(self.speed, self.rect.centery - self.target_y)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLUE, self.rect, 3)

class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed_x = 7 * random.choice((1, -1))
        self.speed_y = 7 * random.choice((1, -1))
        self.fire_color = FIRE_COLORS[0]
        self.particles = []

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # Add current position to trail
        ball_trail.append(self.rect.copy())
        if len(ball_trail) > 10:
            ball_trail.pop(0)
        # Create fire particles
        for _ in range(3):
            self.particles.append(Particle(self.rect.centerx, self.rect.centery, self.fire_color))

    def draw(self):
        for particle in self.particles:
            particle.update()
            particle.draw(screen)
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for trail_rect in ball_trail:
            pygame.draw.ellipse(screen, (*self.fire_color, 128), trail_rect)
        pygame.draw.ellipse(screen, self.fire_color, self.rect)
        pygame.draw.ellipse(screen, BLUE, self.rect, 3)
        
    def reset(self):
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.speed_x *= random.choice((1, -1))
        self.speed_y *= random.choice((1, -1))
        ball_trail.clear()
        self.particles.clear()

    def toggle_fire_color(self):
        self.fire_color = FIRE_COLORS[1] if self.fire_color == FIRE_COLORS[0] else FIRE_COLORS[0]

def fuzzy_ball_position(ball, ai_paddle):
    if ball.rect.centery < ai_paddle.rect.centery - 100:
        return "far"
    elif ball.rect.centery < ai_paddle.rect.centery - 50:
        return "mid"
    else:
        return "near"

def fuzzy_paddle_position(ai_paddle):
    if ai_paddle.rect.centery < SCREEN_HEIGHT // 3:
        return "low"
    elif ai_paddle.rect.centery < 2 * SCREEN_HEIGHT // 3:
        return "mid"
    else:
        return "high"

def fuzzy_ball_speed(ball):
    speed = abs(ball.speed_y)
    if ball.speed_x < 0:
        return "negative"
    elif speed < 4:
        return "slow"
    elif speed < 7:
        return "medium"
    else:
        return "fast"

def fuzzy_logic(ball, ai_paddle):
    ball_pos_fuzzy = fuzzy_ball_position(ball, ai_paddle)
    paddle_pos_fuzzy = fuzzy_paddle_position(ai_paddle)
    ball_speed_fuzzy = fuzzy_ball_speed(ball)
    
    move_direction = "stay"  # Default action

    # Define fuzzy logic rules
    if ball_pos_fuzzy == "near":
        if ball_speed_fuzzy in ["slow", "medium"]:
            move_direction = "down" if ball.rect.centery > ai_paddle.rect.centery else "up"
        elif ball_speed_fuzzy == "fast":
            move_direction = "down" if ball.rect.centery > ai_paddle.rect.centery else "up"
    elif ball_pos_fuzzy == "mid":
        if ball_speed_fuzzy == "fast":
            move_direction = "down" if ball.rect.centery > ai_paddle.rect.centery else "up"
    elif ball_pos_fuzzy == "far":
        if ball_speed_fuzzy == "fast":
            move_direction = "down" if ball.rect.centery > ai_paddle.rect.centery else "up"

    return move_direction

def ai_move(ai_paddle, ball, difficulty='medium'):
    reaction_time = {'easy': 0.2, 'medium': 0.1, 'hard': 0.05}
    #max_speed = {'easy': 7, 'medium': 10, 'hard': 12}
    max_speed = {'easy': 5, 'medium': 7, 'hard': 9}
    #max_speed = {'easy': 4, 'medium': 6, 'hard': 8}
    
    # Adding a random delay to simulate reaction time
    if random.random() < reaction_time[difficulty]:
        return

    # Get fuzzy logic decision
    move_direction = fuzzy_logic(ball, ai_paddle)
    
    if move_direction == "down":
        ai_paddle.move("down")
    elif move_direction == "up":
        ai_paddle.move("up")
    # If the direction is "stay", do nothing
    
    ai_paddle.speed = min(max_speed[difficulty], ai_paddle.speed)



def draw_background():
    for i in range(SCREEN_HEIGHT):
        color = (0, 0, i // 3)
        pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))

def draw_scores(player_score, ai_score):
    player_text = font.render(str(player_score), True, WHITE)
    ai_text = font.render(str(ai_score), True, WHITE)
    player_shadow = font.render(str(player_score), True, BLACK)
    ai_shadow = font.render(str(ai_score), True, BLACK)
    
    screen.blit(player_shadow, (SCREEN_WIDTH//4 + 2, 22))
    screen.blit(ai_shadow, (3 * SCREEN_WIDTH//4 + 2, 22))
    screen.blit(player_text, (SCREEN_WIDTH//4, 20))
    screen.blit(ai_text, (3 * SCREEN_WIDTH//4, 20))

def draw_logs():
    y_offset = SCREEN_HEIGHT - 150  # Start drawing logs from 150 pixels above the bottom
    for log in game_logs[-5:]:  # Display last 5 logs
        log_text = log_font.render(log, True, WHITE)
        log_width = log_text.get_width()
        screen.blit(log_text, ((SCREEN_WIDTH - log_width) // 2, y_offset))
        y_offset += 30

def log_event(event):
    game_logs.append(event)
    print(event)  # Also print to console for debugging

def draw_timer(start_time):
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    timer_text = timer_font.render(f"Time: {minutes:02}:{seconds:02}", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 20))

def main_menu():
    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Start game on Enter key press
                    menu_running = False
                elif event.key == pygame.K_q:  # Quit game on Q key press
                    pygame.quit()
                    quit()

        screen.fill(DARK_BLUE)
        title_text = menu_font.render("Ping Pong Game", True, WHITE)
        start_text = menu_font.render("Press ENTER to Start", True, WHITE)
        quit_text = menu_font.render("Press Q to Quit", True, WHITE)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 400))
        
        pygame.display.flip()

def pause_game():
    global paused
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Resume game on 'P' key press
                    paused = False
                    pause_sound.play()
                elif event.key == pygame.K_q:  # Quit game on 'Q' key press
                    pygame.quit()
                    quit()
        
        screen.fill(DARK_BLUE)
        pause_text = menu_font.render("Game Paused", True, WHITE)
        resume_text = menu_font.render("Press P to Resume", True, WHITE)
        quit_text = menu_font.render("Press Q to Quit", True, WHITE)
        
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 150))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 300))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 400))
        
        pygame.display.flip()

# Create paddles and ball
player_paddle = Paddle(30, SCREEN_HEIGHT // 2 - 50, PLAYER_COLOR)
ai_paddle = Paddle(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 50, AI_COLOR)
ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Initialize scores
player_score = 0
ai_score = 0

# Main game loop
running = True
clock = pygame.time.Clock()

# Display main menu
main_menu()

# Start the timer
start_time = time.time()

#Frames for gameplay video
frames = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause_game()
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_paddle.rect.top > 0:
        player_paddle.move("up")
    if keys[pygame.K_s] and player_paddle.rect.bottom < SCREEN_HEIGHT:
        player_paddle.move("down")
    
    ball.move()
    
    if ball.rect.top <= 0 or ball.rect.bottom >= SCREEN_HEIGHT:
        ball.speed_y *= -1

    if ball.rect.colliderect(player_paddle.rect):
        ball.speed_x *= -1
        ball.toggle_fire_color()
        hit_sound.play()
        log_event("Player hits the ball")

    if ball.rect.colliderect(ai_paddle.rect):
        ball.speed_x *= -1
        ball.toggle_fire_color()
        hit_sound.play()
        log_event("AI hits the ball")

    if ball.rect.left <= 0:
        ai_score += 1
        score_sound.play()
        ball.reset()
        log_event("AI scores")
    elif ball.rect.right >= SCREEN_WIDTH:
        player_score += 1
        score_sound.play()
        ball.reset()
        log_event("Player scores")
    
    ai_move(ai_paddle, ball)
    player_paddle.update()
    ai_paddle.update()
    
    draw_background()
    
    player_paddle.draw()
    ai_paddle.draw()
    ball.draw()
    
    draw_scores(player_score, ai_score)
    draw_logs()
    draw_timer(start_time)
    
    pygame.display.flip()
    
    #capture frames
    # frame = pygame.surfarray.array3d(pygame.display.get_surface())
    # frame = np.flip(frame, axis=0)
    # frame = np.rot90(frame,k=-1)
    # frames.append(frame)

    clock.tick(60)

pygame.quit()

# clips = ImageSequenceClip(frames,fps=60)
# clips.write_videofile("gameplay.mp4",codec = "libx264")
