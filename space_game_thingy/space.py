import pygame
import math
import os

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Space Game")
clock = pygame.time.Clock()

CENTER_X = WIN_WIDTH // 2
CENTER_Y = WIN_HEIGHT // 2

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")



def load_image(name):
    return pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()


def create_ship_surface():
    BASE_DIR = os.path.dirname(__file__)
    IMG_DIR = os.path.join(BASE_DIR, "img")

    surface = pygame.image.load(os.path.join(IMG_DIR, "spaceship.png")).convert_alpha()

    return surface
class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.x = 0
        self.y = 0

        self.target = None

    def follow(self, target):
        self.target = target

    def update(self):
        if self.target:
            self.x = self.target.world_x
            self.y = self.target.world_y

    def apply(self, world_pos):
        wx, wy = world_pos
        sx = wx - self.x + self.width // 2
        sy = wy - self.y + self.height // 2
        return sx, sy

class Ship:
    def __init__(self, image):
        self.world_x = 0
        self.world_y = 0

        self.vx = 0
        self.vy = 0

        self.angle = 0
        self.rotation_speed = 3

        self.thrust = 0.25
        self.friction = 0.98

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

    def draw(self, screen, camera):
        rotated = pygame.transform.rotate(self.image, -self.angle -90)
        screen_pos = camera.apply((self.world_x, self.world_y))
        rect = rotated.get_rect(center=screen_pos)
        screen.blit(rotated, rect)


class Background:
    def __init__(self, image):
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()

    def draw(self, screen, camera):
        offset_x = -camera.x % self.width
        offset_y = -camera.y % self.height

        for x in range(-1, WIN_WIDTH // self.width + 2):
            for y in range(-1, WIN_HEIGHT // self.height + 2):
                screen.blit(self.image,(x * self.width + offset_x, y * self.height + offset_y)) 


def main():
    ship_image = load_image("spaceship.png")
    bg_image = load_image("test_bg.jpg")

    player = Ship(ship_image)
    background = Background(bg_image)

    camera = Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player)

    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)

        camera.update()

        screen.fill((0, 0, 0))
        background.draw(screen, camera)
        player.draw(screen, camera)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

