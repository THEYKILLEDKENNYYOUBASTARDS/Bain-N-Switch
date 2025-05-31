import pygame
import math
import random
from pygame import transform, image

# Initialize pygame
pygame.init()

# Game constants
fps = 60
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
clock = pygame.time.Clock()

# Load images
try:
    bgs = transform.scale(image.load('bg.jpg'), (900, 800))
    banners = transform.scale(image.load('meter.png'), (100, 700))
    guns = transform.scale(image.load('aim.png'), (100, 100))
    target_images = [
        transform.scale(image.load('enemy.png'), (120, 80)),
        transform.scale(image.load('enemy.png'), (102, 68)),
        transform.scale(image.load('enemy.png'), (84, 56))
    ]
    boss_image = transform.scale(image.load('enemy.png'), (200, 150))  # Larger image for boss
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    exit()

# Game settings
targets = {
    1: [10, 5, 3],  # Level 1 target counts
    2: [12, 8, 5],  # Level 2 target counts
    3: [15, 12, 8, 3],  # Level 3 target counts
    4: [1]  # Level 4 has just the boss
}

level = 1
score = 0
font = pygame.font.SysFont('Arial', 30)

class Target:
    def __init__(self, x, y, size, speed, level):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.level = level
        self.active = True
        self.direction = random.choice([-1, 1])
        self.health = 1  # Regular targets have 1 health
        self.max_health = 1
        self.rect = pygame.Rect(x, y, size, size)
    
    def update(self):
        if not self.active:
            return False
        
        # Move target
        self.x += self.speed * self.direction
        
        # Reverse direction at screen edges
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.direction *= -1
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        return True
    
    def draw(self):
        if self.active:
            if self.level == 4:  # Boss
                screen.blit(boss_image, (self.x, self.y))
                # Draw health bar
                health_bar_width = 100
                health_ratio = self.health / self.max_health
                pygame.draw.rect(screen, (255, 0, 0), (self.x + 50, self.y - 20, health_bar_width, 10))
                pygame.draw.rect(screen, (0, 255, 0), (self.x + 50, self.y - 20, health_bar_width * health_ratio, 10))
            else:
                screen.blit(target_images[self.level - 1], (self.x, self.y))

class Boss(Target):
    def __init__(self, x, y):
        super().__init__(x, y, 200, 15, 4)  # Larger size, slower base speed
        self.health = 1000  # Boss has 5 health
        self.max_health = 1000
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(30, 90)  # Random interval for direction changes
        self.x_speed = random.uniform(2.0, 4.0) * random.choice([-1, 1])  # Random initial x speed
        self.y_speed = random.uniform(2.0, 4.0) * random.choice([-1, 1])  # Random initial y speed
        self.target_x = random.randint(100, WIDTH - 100)
        self.target_y = random.randint(100, HEIGHT - 300)
    
    def update(self):
        if not self.active:
            return False
        
        # Update direction change timer
        self.direction_change_timer += 1
        
        # Change direction randomly
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction_change_timer = 0
            self.direction_change_interval = random.randint(30, 90)
            
            # 50% chance to change direction
            if random.random() < 0.5:
                self.x_speed = random.uniform(2.0, 4.0) * random.choice([-1, 1])
                self.y_speed = random.uniform(2.0, 4.0) * random.choice([-1, 1])
            
            # 30% chance to set a new target position
            if random.random() < 0.3:
                self.target_x = random.randint(100, WIDTH - 100)
                self.target_y = random.randint(100, HEIGHT - 300)
        
        # Move toward target position with some randomness
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Add some randomness to movement
        self.x += self.x_speed + random.uniform(-0.5, 0.5)
        self.y += self.y_speed + random.uniform(-0.5, 0.5)
        
        # Bounce off screen edges
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.x_speed *= -1
            self.target_x = random.randint(100, WIDTH - 100)
        
        if self.y <= 50 or self.y >= HEIGHT - 250:
            self.y_speed *= -1
            self.target_y = random.randint(100, HEIGHT - 300)
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        return True

def init_targets():
    all_targets = []
    
    if level == 1:
        my_list = targets[1]
        for i in range(3):
            for j in range(my_list[i]):
                size = 60 - i * 12
                speed = random.uniform(1.0, 2.0)
                x = WIDTH // (my_list[i] + 1) * (j + 1)
                y = 300 - (i * 150) + 30 * (j % 2)
                all_targets.append(Target(x, y, size, speed, level))
    
    elif level == 2:
        my_list = targets[2]
        for i in range(3):
            for j in range(my_list[i]):
                size = 50 - i * 10
                speed = random.uniform(1.5, 2.5)
                x = WIDTH // (my_list[i] + 1) * (j + 1)
                y = 300 - (i * 150) + 30 * (j % 2)
                all_targets.append(Target(x, y, size, speed, level))
    
    elif level == 3:
        my_list = targets[3]
        for i in range(4):
            for j in range(my_list[i]):
                size = 40 - i * 8
                speed = random.uniform(2.0, 3.0)
                x = WIDTH // (my_list[i] + 1) * (j + 1)
                y = 300 - (i * 100) + 30 * (j % 2)
                all_targets.append(Target(x, y, size, speed, level))
    
    elif level == 4:
        # Create the boss in a random position
        boss_x = random.randint(100, WIDTH - 100)
        boss_y = random.randint(100, HEIGHT - 300)
        boss = Boss(boss_x, boss_y)
        all_targets.append(boss)
    
    return all_targets

# [Rest of the code remains the same...]

all_targets = init_targets()
spawn_timer = 0
spawn_delay = 1000  # milliseconds
last_spawn_time = pygame.time.get_ticks()

def draw_gun():
    mouse_pos = pygame.mouse.get_pos()
    gun_point = (WIDTH / 2, HEIGHT - 200)
    lasers = ['red', 'purple', 'green', 'orange']  # Added orange for level 4
    
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
    else:
        slope = -100000
    
    angle = math.atan(slope)
    rotation = math.degrees(angle)
    
    clicks = pygame.mouse.get_pressed()
    
    if mouse_pos[0] < WIDTH / 2:
        gun = pygame.transform.flip(guns, True, False)
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
                check_hits(mouse_pos)
    else:
        gun = guns
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
                check_hits(mouse_pos)

def check_hits(mouse_pos):
    global score, all_targets
    hit = False
    mouse_rect = pygame.Rect(mouse_pos[0] - 5, mouse_pos[1] - 5, 10, 10)
    
    for target in all_targets:
        if target.active and mouse_rect.colliderect(target.rect):
            if target.level == 4:  # Boss takes multiple hits
                target.health -= 1
                if target.health <= 0:
                    target.active = False
                    score += 200  # Big points for defeating boss
            else:
                target.active = False
                score += (4 - level) * 10  # More points for harder levels
            hit = True
    
    if hit:
        # Play hit sound if available
        pass

def spawn_targets():
    global all_targets, last_spawn_time
    current_time = pygame.time.get_ticks()
    
    if level != 4:  # Don't respawn targets in boss level
        if current_time - last_spawn_time > spawn_delay and len(all_targets) < sum(targets[level]):
            last_spawn_time = current_time
            all_targets = init_targets()

def check_level_complete():
    global level, all_targets
    active_targets = sum(1 for target in all_targets if target.active)
    
    if active_targets == 0:
        if level < 4:
            level += 1
            all_targets = init_targets()
        else:
            # Game complete, restart from level 1
            level = 1
            all_targets = init_targets()

run = True
while run:
    clock.tick(fps)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                level = 1
                all_targets = init_targets()
            elif event.key == pygame.K_2:
                level = 2
                all_targets = init_targets()
            elif event.key == pygame.K_3:
                level = 3
                all_targets = init_targets()
            elif event.key == pygame.K_4:
                level = 4
                all_targets = init_targets()
    
    # Game logic
    spawn_targets()
    
    # Update targets
    active_targets = 0
    for target in all_targets:
        if target.update():
            active_targets += 1
    
    # Check if level is complete
    check_level_complete()
    
    # Drawing
    screen.fill('black')
    screen.blit(bgs, (0, 0))
    screen.blit(banners, (0, HEIGHT - 200))
    
    # Draw targets
    for target in all_targets:
        target.draw()
    
    # Draw gun
    if level > 0:
        draw_gun()
    
    # Draw score
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    # Draw level info
    level_text = font.render(f'Level: {level}', True, (255, 255, 255))
    screen.blit(level_text, (10, 50))
    
    # Special message for boss level
    if level == 4:
        boss_text = font.render("BOSS LEVEL!", True, (255, 0, 0))
        screen.blit(boss_text, (WIDTH // 2 - 70, 20))
    
    pygame.display.flip()

pygame.quit()
