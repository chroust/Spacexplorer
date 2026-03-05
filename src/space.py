import pygame
import math
import os
import random

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Space Game")
clock = pygame.time.Clock()

CENTER_X = WIN_WIDTH // 2
CENTER_Y = WIN_HEIGHT // 2

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")

seed = "seedyseed"
chunk_size = 2000

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
        self.rotation_speed = 4
        self.target_angle = 0

        self.thrust = 0.25
        self.friction = 0.98

        self.image = image

    def update(self, keys, unpress):
        if keys[pygame.K_a]:
            self.target_angle -= self.rotation_speed
        if keys[pygame.K_d]:
            self.target_angle += self.rotation_speed


        self.angle = self.angle + 0.035 *(self.target_angle - self.angle)

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
    
class dfSpaceObject:
    def __init__(self, x, y, type):
        self.world_x = x
        self.world_y = y
        self.type = type

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        pygame.draw.circle(screen, (0, 255, 0), screen_pos, 20)

class WorldManager:
    def __init__(self, chunk_size, seed):
        self.chunk_size = chunk_size
        self.generated_chunks = {}
        self.world_seed = seed

    def get_chunk_coords(self, wx, wy):
        cx = int(wx // self.chunk_size)
        cy = int(wy // self.chunk_size)
        #print(cx, cy)
        return cx, cy
        

    def generate_chunk(self, cx, cy):
        if (cx, cy) in self.generated_chunks:
            return

        seed_string = f"{self.world_seed}_{cx}_{cy}"
        random.seed(seed_string)

        objects_in_chunk = []
        
        # 20% sance
        if random.random() < 0.20:
            obj_x = cx * self.chunk_size + random.randint(0, self.chunk_size)
            obj_y = cy * self.chunk_size + random.randint(0, self.chunk_size)
            objects_in_chunk.append(dfSpaceObject(obj_x, obj_y, "object"))

        self.generated_chunks[(cx, cy)] = objects_in_chunk

    def update(self, player_x, player_y):
        cx, cy = self.get_chunk_coords(player_x, player_y)
        
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                self.generate_chunk(x, y)
                

    def draw(self, screen, camera):
        cx, cy = self.get_chunk_coords(camera.x, camera.y)
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                if (x, y) in self.generated_chunks:
                    for obj in self.generated_chunks[(x, y)]:
                        obj.draw(screen, camera)


def main():
    ship_image = load_image("spaceship.png")
    bg_image = load_image("test_bg.jpg")

    player = Ship(ship_image)
    background = Background(bg_image)

    camera = Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player)

    running = True

    world = WorldManager(chunk_size, seed)

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                unpress = True

        keys = pygame.key.get_pressed()
        unpress = pygame.key.get_just_released()
        player.update(keys, unpress)

        camera.update()

        screen.fill((0, 0, 0))
        background.draw(screen, camera)
        world.draw(screen, camera)
        player.draw(screen, camera)

        world.update(player.world_x, player.world_y)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

