import pygame
import random

# Initialize Pygame
pygame.init()

# Initialize joystick module
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

# Set the window dimensions
window_width = 800
window_height = 600

# Set colors
LIGHT_BLUE = (135, 206, 250)
DARK_PURPLE = (64, 0, 128)
yellow = (255, 255, 0)
green = (0, 255, 0)

class Cube(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(yellow)
        self.rect = self.image.get_rect()
        self.rect.x = (window_width // 4) - (size // 2)
        self.rect.y = (window_height // 2) - (size // 2)
        self.velocity = 0
        self.gravity = 0.5
        self.jump_velocity = -10

    def update(self):
        self.velocity += self.gravity
        self.rect.y += self.velocity

        if self.rect.bottom > window_height:
            self.rect.bottom = window_height
            self.velocity = 0

    def jump(self):
        self.velocity = self.jump_velocity

class VerticalBar(pygame.sprite.Sprite):
    global bg_color
    def __init__(self, width, height, speed, opening_size):
        super().__init__()
        self.width = width
        self.height = height
        self.speed = speed
        self.opening_size = opening_size
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = window_width
        self.opening_y = random.randint(0, height - opening_size)

    def update(self):
        self.rect.x -= self.speed

        if self.rect.right < 0:
            self.rect.left = window_width
            self.opening_y = random.randint(0, self.height - self.opening_size)

    def draw(self, screen):
        pygame.draw.rect(screen, green, (self.rect.x, 0, self.width, self.opening_y))
        pygame.draw.rect(screen, green, (self.rect.x, self.opening_y + self.opening_size, self.width, self.height - self.opening_y - self.opening_size))
        pygame.draw.rect(screen, LIGHT_BLUE, (self.rect.x, self.opening_y, self.width, self.opening_size))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Jumping Cube")
        self.clock = pygame.time.Clock()
        self.cube = Cube(50)
        self.bar = VerticalBar(60, window_height, 4, int(self.cube.size * 4))
        self.all_sprites = pygame.sprite.Group(self.cube, self.bar)

    def display_jump_counter(self, count, high_score):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {count}", True, (255, 255, 255))
        high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect()
        high_score_rect = high_score_text.get_rect()
        score_rect.topleft = (10, 10)
        high_score_rect.topleft = (10, 50)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_score_text, high_score_rect)

    def save_score(self, score):
        try:
            with open("flappy_bird/high_score.txt", "r") as file:
                high_score = int(file.read())
        except FileNotFoundError:
            high_score = 0

        if score > high_score:
            with open("flappy_bird/high_score.txt", "w") as file:
                file.write(str(score))
            high_score = score

        return high_score


    def run(self):
        try:
            with open('flappy_bird/high_score.txt', 'r') as file:
                high_score = int(file.read())
        except FileNotFoundError:
            high_score = 0

        running = True
        start_time = pygame.time.get_ticks()
        jump_count = 0
        speed_increment = 0

        if not joysticks:
            print("No controller detected. Running with keyboard controls.")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.cube.jump()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A button (button 1)
                        self.cube.jump()
                    elif event.button == 1:  # B button (button 2)
                        running = False

            self.all_sprites.update()

            if self.bar.rect.right < self.cube.rect.left:
                jump_count += 1

            # Increase the speed of the vertical bars every 200 points
                if jump_count % 200 == 0:
                    speed_increment += 1
                    self.bar.speed += speed_increment

            if pygame.sprite.collide_rect(self.cube, self.bar):
                if self.cube.rect.y < self.bar.opening_y or self.cube.rect.bottom > self.bar.opening_y + self.bar.opening_size:
                    running = False  # Game over
                    high_score = self.save_score(jump_count)

        # Calculate the elapsed time in seconds
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0

        # Calculate the interpolation factor based on the elapsed time and cycle duration
            cycle_duration = 90.0
            t = (elapsed_time % cycle_duration) / cycle_duration

        # Interpolate between light blue and dark purple colors
            if t < 0.5:
                interpolation_factor = t * 2
                bg_color = tuple(int(start * (1 - interpolation_factor) + end * interpolation_factor)
                             for start, end in zip(LIGHT_BLUE, DARK_PURPLE))
            else:
                interpolation_factor = (t - 0.5) * 2
                bg_color = tuple(int(start * (1 - interpolation_factor) + end * interpolation_factor)
                             for start, end in zip(DARK_PURPLE, LIGHT_BLUE))

        # Fill the background with the interpolated color
            self.screen.fill(bg_color)

            self.bar.draw(self.screen)
            self.all_sprites.draw(self.screen)

            self.display_jump_counter(jump_count, high_score)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()

pygame.quit()