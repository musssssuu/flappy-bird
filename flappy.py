import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800  # Adjusted for full screen
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Bird properties
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_INITIAL_X = SCREEN_WIDTH // 3
BIRD_INITIAL_Y = SCREEN_HEIGHT // 2
GRAVITY = 0.25
FLAP_STRENGTH = 6

# Pipe properties
PIPE_WIDTH = 70
PIPE_GAP = 140  # Initial gap size
PIPE_SPEED = 3
PIPE_FREQUENCY = 1000  # Reduced frequency

# Coin properties
COIN_SIZE = 20
COIN_SPEED = 3
COIN_FREQUENCY = 300

# Difficulty properties
DIFFICULTY_INCREASE_INTERVAL = 5
PIPE_DISTANCE_DECREASE_AMOUNT = 10
INITIAL_PIPE_DISTANCE = 250  # Initial distance between pipes

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Flappy Bird")

# Load images
bird_img = pygame.image.load('bird.png').convert_alpha()  # Convert image to use alpha transparency
bird_img = pygame.transform.scale(bird_img, (BIRD_WIDTH, BIRD_HEIGHT))

pipe_img = pygame.Surface((PIPE_WIDTH, SCREEN_HEIGHT))
pipe_img.fill((0, 255, 0))

coin_img = pygame.Surface((COIN_SIZE, COIN_SIZE))
coin_img.fill(YELLOW)

background_img = pygame.image.load('background.png')
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock to control the game's frame rate
clock = pygame.time.Clock()

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0

    def flap(self):
        self.velocity = -FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        screen.blit(bird_img, (self.x, self.y))

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, 400)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def off_screen(self):
        return self.x < -PIPE_WIDTH

    def draw(self):
        # Draw top pipe
        screen.blit(pipe_img, (self.x, self.height - SCREEN_HEIGHT - PIPE_GAP // 2))
        # Draw bottom pipe
        bottom_pipe_y = self.height + PIPE_GAP // 2
        screen.blit(pipe_img, (self.x, bottom_pipe_y))

    def collide(self, bird):
        if bird.y < 0 or bird.y > SCREEN_HEIGHT:
            return True

        if bird.x + BIRD_WIDTH > self.x and bird.x < self.x + PIPE_WIDTH:
            if bird.y < self.height - PIPE_GAP // 2 or bird.y + BIRD_HEIGHT > self.height + PIPE_GAP // 2:
                return True

        return False

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = True  # Add a flag to track visibility

    def update(self):
        self.x -= COIN_SPEED
        if self.x < -COIN_SIZE:
            self.visible = False  # Hide the coin if it goes off-screen

    def draw(self):
        if self.visible:
            screen.blit(coin_img, (self.x, self.y))


bird = Bird(BIRD_INITIAL_X, BIRD_INITIAL_Y)
pipes = []
coins = []

score = 0
high_score = 0
font = pygame.font.Font(None, 36)

game_over = False
restart_button_rect = pygame.Rect(150, 250, 100, 50)
exit_button_rect = pygame.Rect(700, 10, 90, 30)

pipes_passed = 0
running = True
while running:
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird.flap()
            if event.key == pygame.K_SPACE and game_over:
                bird = Bird(BIRD_INITIAL_X, BIRD_INITIAL_Y)
                pipes = []
                coins = []  # Reset coins
                score = 0
                game_over = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    if not game_over:
        bird.update()

        if len(pipes) == 0 or pipes[-1].x < SCREEN_WIDTH - PIPE_FREQUENCY:
            pipes.append(Pipe(SCREEN_WIDTH))
            pipes.append(Pipe(SCREEN_WIDTH + PIPE_WIDTH + 150))  # Add new pipe
            pipes_passed += 1
            if pipes_passed % DIFFICULTY_INCREASE_INTERVAL == 0:
                PIPE_GAP -= PIPE_DISTANCE_DECREASE_AMOUNT  # Decrease pipe gap

        # Add coins
        if random.randint(0, COIN_FREQUENCY) == 0:
            coin_y = random.randint(50, SCREEN_HEIGHT - 50 - COIN_SIZE)  # Adjusted range
            coins.append(Coin(SCREEN_WIDTH, coin_y))

        for pipe in pipes:
            pipe.update()
            if pipe.off_screen():
                pipes.remove(pipe)
                continue
            if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                pipe.passed = True
                score += 1
                if pipes_passed % DIFFICULTY_INCREASE_INTERVAL == 0:
                    PIPE_FREQUENCY -= PIPE_DISTANCE_DECREASE_AMOUNT
            if pipe.collide(bird):
                game_over = True
                if score > high_score:
                    high_score = score

        # Update and draw coins
        for coin in coins:
            coin.update()
            coin.draw()

        # Check for collision with coins
        for coin in coins:
            if coin.x < bird.x + BIRD_WIDTH < coin.x + COIN_SIZE and \
               coin.y < bird.y + BIRD_HEIGHT < coin.y + COIN_SIZE:
                score += 2
                coins.remove(coin)

        if game_over:
            continue

    bird.draw()
    for pipe in pipes:
        pipe.draw()

    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    high_score_text = font.render(f"High Score: {int(high_score)}", True, WHITE)
    screen.blit(high_score_text, (10, 50))

    if game_over:
        restart_text = font.render("Restart", True, WHITE)
        pygame.draw.rect(screen, BLACK, restart_button_rect)
        screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2,
                                   restart_button_rect.centery - restart_text.get_height() // 2))

        mouse_pos = pygame.mouse.get_pos()
        if restart_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, WHITE, restart_button_rect, 2)
            if pygame.mouse.get_pressed()[0]:
                bird = Bird(BIRD_INITIAL_X, BIRD_INITIAL_Y)
                pipes = []
                coins = []  # Reset coins
                score = 0
                game_over = False
        else:
            pygame.draw.rect(screen, WHITE, restart_button_rect, 2)

    pygame.draw.rect(screen, BLACK, exit_button_rect)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(exit_text, (exit_button_rect.centerx - exit_text.get_width() // 2,
                             exit_button_rect.centery - exit_text.get_height() // 2))
    pygame.draw.rect(screen, WHITE, exit_button_rect, 2)

    # Write name "Mustafa" at the top
    name_text = font.render("Mustafa", True, WHITE)
    screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
