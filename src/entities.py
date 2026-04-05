import pygame
import math

class Ship:
    def __init__(self, image, mask):
        self.world_x, self.world_y = 0, 0
        self.vx, self.vy = 0, 0
        self.angle = -90
        self.rotation_speed = 4
        self.target_angle = -90
        self.thrust = 0.25
        self.friction = 0.98
        self.image = image
        self.mask = mask
        self.fuel_max = 1000
        self.fuel = self.fuel_max
        self.fuel_consumption = 30
        self.credits = 0
        self.upgrade_levels = {}
        self.is_mining = False

    def update(self, keys, unpress, delta_time):
        if keys[pygame.K_a]: self.target_angle -= self.rotation_speed
        if keys[pygame.K_d]: self.target_angle += self.rotation_speed

        self.angle = self.angle + 0.035 * (self.target_angle - self.angle)

        if keys[pygame.K_w] and self.fuel > 0:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.thrust
            self.vy += math.sin(rad) * self.thrust
            self.fuel -= self.fuel_consumption * delta_time

        self.world_x += self.vx
        self.world_y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def refill_fuel(self, amount):
        self.fuel = min(self.fuel + amount, self.fuel_max)

    def draw(self, screen, camera):
        rotated = pygame.transform.rotate(self.image, -self.angle - 90)
        screen_pos = camera.apply((self.world_x, self.world_y))
        rect = rotated.get_rect(center=screen_pos)
        screen.blit(rotated, rect)

class dfSpaceObject:
    def __init__(self, x, y, mask=None):
        self.type = "dfSpaceObject"
        self.size = 20
        self.gravity = 0.5
        self.gravity_range = 500
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.highlighted = False
        self.mine_rate = 0
        self.mine_range = 0

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        color = (0, 255, 0)
        if self.highlighted:
            color = (255, 255, 0)
            pygame.draw.circle(screen, (255, 255, 0), screen_pos, self.size + 5, 2)
        pygame.draw.circle(screen, color, screen_pos, self.size)

class planet:
    def __init__(self, x, y, mask=None):
        self.type = "planet"
        self.size = 200
        self.gravity = 2
        self.gravity_range = 1000
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.is_mining = False
        self.mine_rate = 8
        self.mine_range = 300

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        pygame.draw.circle(screen, (0, 100, 255), screen_pos, self.size)
        if self.is_mining:
            pygame.draw.circle(screen, (255, 220, 50), screen_pos, self.size + 8, 3)

class asteriod:
    def __init__(self, x ,y, mask=None):
        self.type = "asteroid"
        self.size = 25
        self.gravity = 0
        self.gravity_range = 0
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.is_mining = False
        self.mine_rate = 20
        self.mine_range = 90

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        pygame.draw.circle(screen, (168, 104, 0), screen_pos, self.size)
        if self.is_mining:
            pygame.draw.circle(screen, (255, 220, 50), screen_pos, self.size + 6, 2)