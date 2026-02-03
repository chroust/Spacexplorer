import pygame
import math
import os

pygame.init()

win_width, win_height = 1280, 720
screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("space Game")
clock = pygame.time.Clock()

center_x = win_width // 2
center_y = win_height // 2

def create_ship_surface():
    BASE_DIR = os.path.dirname(__file__)
    IMG_DIR = os.path.join(BASE_DIR, "img")

    surface = pygame.image.load(os.path.join(IMG_DIR, "spaceship.png")).convert_alpha()

    return surface

def bg():
    BASE_DIR = os.path.dirname(__file__)
    IMG_DIR = os.path.join(BASE_DIR, "img")

    bg = pygame.image.load(os.path.join(IMG_DIR, "test_bg.jpg")).convert_alpha()

    return bg

class Ship:
    def __init__(self, image):

        self.world_x = 0
        self.world_y = 0

        self.vx = 0
        self.vy = 0

        self.angle = 0
        self.rotation_speed = 3

        self.thrust = 0.25
        self.friction = 0.5

        self.image = image

    def update(self, keys):

        if keys[pygame.K_a]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_d]:
            self.angle += self.rotation_speed

        if keys[pygame.K_w]:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.thrust
            self.vy += math.sin(rad) * self.thrust

        self.world_x += self.vx
        self.world_y += self.vy

        self.vx *= self.friction
        self.vy *= self.friction

        print(self.world_x, " / ", self.world_y)

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(center_x, center_y))
        screen.blit(rotated, rect)

def main():
    running = True

    ship_image = create_ship_surface()
    bg_image = bg()
    player = Ship(ship_image)

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)

        screen.fill((0, 0, 0))
        #screen.blit(bg_image, (0, 0) - player.position (100, 500), )
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
