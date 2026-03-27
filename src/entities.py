import pygame
import math

class Ship:
    def __init__(self, image):
        self.world_x, self.world_y = 0, 0
        self.vx, self.vy = 0, 0
        self.angle = -90
        self.rotation_speed = 4
        self.target_angle = -90
        self.thrust = 0.25
        self.friction = 0.98
        self.image = image

    def update(self, keys, unpress):
        if keys[pygame.K_a]: self.target_angle -= self.rotation_speed
        if keys[pygame.K_d]: self.target_angle += self.rotation_speed

        self.angle = self.angle + 0.035 * (self.target_angle - self.angle)

        if keys[pygame.K_w]:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.thrust
            self.vy += math.sin(rad) * self.thrust

        self.world_x += self.vx
        self.world_y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def draw(self, screen, camera):
        rotated = pygame.transform.rotate(self.image, -self.angle - 90)
        screen_pos = camera.apply((self.world_x, self.world_y))
        rect = rotated.get_rect(center=screen_pos)
        screen.blit(rotated, rect)

class dfSpaceObject:
    def __init__(self, x, y, type):
        self.world_x, self.world_y = x, y
        self.type = type
        self.size = 20

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        pygame.draw.circle(screen, (0, 255, 0), screen_pos, self.size)

class planet:
    def __init__(self, x, y):
        self.size = 300
        self.world_x, self.world_y = x, y

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        pygame.draw.circle(screen, (0, 100, 255), screen_pos, self.size)