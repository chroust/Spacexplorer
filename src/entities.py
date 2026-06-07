import pygame
import math
import random
from . import utils

PLANET_SPRITES: list[str] = [
    "planets/red_planet.png",
    "planets/purple_planet.png",
    "planets/purple_green_planet.png"
]

class Ship:
    def __init__(self, image, mask, spritesheet_name="spaceship_spritesheet.png", 
                 frame_width=36, frame_height=75, frame_duration=0.08):
        self.world_x, self.world_y = 0, 0
        self.vx, self.vy = 0, 0
        self.angle = -90
        self.rotation_speed = 4
        self.target_angle = -90
        self.thrust = 0.25
        self.friction = 0.98
        self.image = image
        self.mask = mask
        self.radius = max(image.get_width(), image.get_height()) / 2
        self.fuel_max = 1000
        self.fuel = self.fuel_max
        self.fuel_consumption = 30
        self.health_max = 100
        self.health = self.health_max
        self.damage_cooldown = 0.6
        self.damage_timer = 0.0
        self.credits = 0
        self.upgrade_levels = {}
        self.is_mining = False
        
        # Animation attr
        self.spritesheet_frames = utils.load_spritesheet(spritesheet_name, frame_width, frame_height)
        self.animation = utils.AnimationController(
            self.spritesheet_frames,
            frame_duration=frame_duration,
            loop=True,
            start_frame=0,
            loop_start_frame=1,
        )
        self.is_moving = False

    def update(self, keys, unpress, delta_time):
        if keys[pygame.K_a]: self.target_angle -= self.rotation_speed
        if keys[pygame.K_d]: self.target_angle += self.rotation_speed

        self.angle = self.angle + 0.035 * (self.target_angle - self.angle)

        self.is_moving = keys[pygame.K_w] and self.fuel > 0
        if self.is_moving:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.thrust
            self.vy += math.sin(rad) * self.thrust
            self.fuel -= self.fuel_consumption * delta_time
            self.animation.play()
        else:
            self.animation.stop()
            self.animation.reset()

        self.damage_timer = max(self.damage_timer - delta_time, 0.0)

        self.world_x += self.vx
        self.world_y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Update
        self.animation.update(delta_time)

    def refill_fuel(self, amount):
        self.fuel = min(self.fuel + amount, self.fuel_max)

    def take_damage(self, amount):
        if self.damage_timer > 0:
            return False
        self.health = max(self.health - amount, 0)
        self.damage_timer = self.damage_cooldown
        return True

    def heal(self, amount):
        self.health = min(self.health + amount, self.health_max)

    def draw(self, screen, camera):
        current_frame = self.animation.get_current_frame()
        draw_image = current_frame if current_frame else self.image
        
        rotated = pygame.transform.rotate(draw_image, -self.angle - 90)
        screen_pos = camera.apply((self.world_x, self.world_y))
        rect = rotated.get_rect(center=screen_pos)
        screen.blit(rotated, rect)

REFUEL_STATION_SPRITES = [
    "refuel_station/refuel_station.png",
    "refuel_station/station_barrel.png",
    "refuel_station/station_beacon.png",
    "refuel_station/station_pad.png",
    "refuel_station/station_pump.png",
]

ENEMY_SPRITES = [
    "enemy/blade_saw.png",
    "enemy/blade_shuriken.png",
    "enemy/blade_tri.png",
    "enemy/drone_fighter.png",
    "enemy/drone_saucer.png",
    "enemy/drone_skull.png",
    "enemy/enemy_blade.png",
    "enemy/enemy_drone.png",
]

ASTEROID_SPRITES: list[str] = [
    "asteroids/asteroid.png",
    "asteroids/ice_asteroid.png"
]

class dfSpaceObject:
    def __init__(self, x, y, mask=None):
        self.type = "dfSpaceObject"
        self.world_x, self.world_y = x, y
        self.gravity = 0.5
        self.gravity_range = 500
        self.highlighted = False
        self.mine_rate = 0
        self.mine_range = 0
        self.collision_damage = 0
        self.total_fuel = 500 
        self.fuel_remaining = self.total_fuel 

        self.image = utils.load_sprite_variant(REFUEL_STATION_SPRITES)
        if self.image is not None:
            self.mask = utils.create_mask_from_img(self.image)
            self.width, self.height = self.image.get_size()
            self.radius = max(self.width, self.height) / 2
            self.size = int(self.radius)
        else:
            self.mask = mask
            self.size = 20
            self.radius = self.size

    def get_mask(self):
        return self.mask

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        if self.image is not None:
            rect = self.image.get_rect(center=screen_pos)
            screen.blit(self.image, rect)
            if self.highlighted:
                pygame.draw.circle(screen, (255, 255, 0), screen_pos, int(self.radius) + 8, 2)
        else:
            color = (0, 255, 0)
            if self.highlighted:
                color = (255, 255, 0)
                pygame.draw.circle(screen, (255, 255, 0), screen_pos, self.size + 5, 2)
            pygame.draw.circle(screen, color, screen_pos, self.size)

class EnemyShip:
    def __init__(self, x, y, mask=None):
        self.type = "enemy"
        self.world_x, self.world_y = x, y
        self.gravity = 0
        self.gravity_range = 0
        self.vx, self.vy = 0, 0
        self.angle = 0
        self.target_angle = 0
        self.rotation_speed = 3
        self.thrust = 0.18
        self.friction = 0.97
        self.collision_damage = 20
        self.health = 1
        self.active = True
        self.chase_range = 1500
        self.despawn_range = 3500

        self.image = utils.load_sprite_variant(ENEMY_SPRITES)
        if self.image is not None:
            self.mask = utils.create_mask_from_img(self.image)
            self.width, self.height = self.image.get_size()
            self.radius = max(self.width, self.height) / 2
            self.size = int(self.radius)
        else:
            self.mask = mask
            self.size = 30
            self.radius = self.size

        self._mask_cache = None
        self._mask_cache_angle = None

    def get_mask(self):
        if self.image is None:
            return self.mask
        if self._mask_cache is not None and self._mask_cache_angle == self.angle:
            return self._mask_cache
        rotated = pygame.transform.rotate(self.image, -self.angle - 90)
        self._mask_cache = pygame.mask.from_surface(rotated)
        self._mask_cache_angle = self.angle
        return self._mask_cache

    def update(self, player, delta_time, game_time):
        if not self.active:
            return

        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = math.hypot(dx, dy)

        if distance > self.despawn_range:
            self.active = False
            return

        if distance <= self.chase_range:
            self.target_angle = math.degrees(math.atan2(dy, dx))
            self.angle += 0.05 * (self.target_angle - self.angle)
            rad = math.radians(self.angle)
            speed_boost = 1.0 + (game_time / 60.0) * 0.1
            self.vx += math.cos(rad) * self.thrust * speed_boost * delta_time * 60
            self.vy += math.sin(rad) * self.thrust * speed_boost * delta_time * 60

        self.world_x += self.vx
        self.world_y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def take_damage(self, amount):
        if not self.active:
            return False
        self.health = max(self.health - amount, 0)
        if self.health <= 0:
            self.active = False
            return True
        return False

    def draw(self, screen, camera):
        if not self.active:
            return
        screen_pos = camera.apply((self.world_x, self.world_y))
        if self.image is not None:
            rotated = pygame.transform.rotate(self.image, -self.angle - 90)
            rect = rotated.get_rect(center=screen_pos)
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (200, 30, 30), screen_pos, self.size)
            pygame.draw.circle(screen, (255, 255, 255), screen_pos, self.size, 2)

class BlackHole:
    def __init__(self, x, y, mask=None, spritesheet_name="black_hole_spritesheet.png",
                 frame_width=120, frame_height=92, frame_duration=0.1):
        self.type = "blackhole"
        self.size = random.randint(20, 170)
        self.radius = self.size
        self.gravity = 10.0
        self.gravity_range = self.size * 10
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.collision_damage = 9999
        self.is_mining = False
        
        # Animation attr
        try:
            self.spritesheet_frames = utils.load_spritesheet(spritesheet_name, frame_width, frame_height)
            self.animation = utils.AnimationController(
                self.spritesheet_frames,
                frame_duration=frame_duration,
                loop=True,
                end_frame=31,
            )
            self.animation.play()
        except Exception:
            # Fallback if doesn't exist
            self.spritesheet_frames = []
            self.animation = None

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        
        #draw animated frame
        if self.animation and self.animation.get_current_frame():
            frame = self.animation.get_current_frame()
            scale_factor = (self.size * 2) / frame.get_width()
            scaled_frame = pygame.transform.scale(frame, 
                                                  (int(frame.get_width() * scale_factor),
                                                   int(frame.get_height() * scale_factor)))
            rect = scaled_frame.get_rect(center=screen_pos)
            screen.blit(scaled_frame, rect)
        else:
            #original drawing if no animation
            pygame.draw.circle(screen, (10, 10, 10), screen_pos, self.size)
            pygame.draw.circle(screen, (120, 0, 180), screen_pos, int(self.size * 0.8), 3)
            pygame.draw.circle(screen, (190, 0, 255), screen_pos, int(self.size * 0.45), 2)

class planet:
    def __init__(self, x, y, mask=None):
        self.type = "planet"
        self.size = 200
        self.radius = self.size
        self.gravity = 2
        self.gravity_range = 1000
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.is_mining = False
        self.mine_rate = 8
        self.mine_range = 300
        self.collision_damage = 30
        self.total_mineable = 200 
        self.ore_remaining = self.total_mineable 

        self.image = utils.load_sprite_variant(PLANET_SPRITES)
        if self.image is not None:
            scalesize = (self.size * 2, self.size * 2)
            self.image = pygame.transform.scale(self.image, scalesize)
            self.mask = utils.create_mask_from_img(self.image)
            self.width, self.height = self.image.get_size()
            self.radius = max(self.width, self.height) / 2
        else:
            self.image = None

    def get_mask(self):
        return self.mask

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        if getattr(self, 'image', None) is not None:
            rect = self.image.get_rect(center=screen_pos)
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, (168, 104, 0), screen_pos, self.size)
        if self.is_mining:
            pygame.draw.circle(screen, (255, 220, 50), screen_pos, self.size + 8, 3)

class asteriod:
    def __init__(self, x ,y, mask=None):
        self.type = "asteroid"
        self.size = 25
        self.radius = self.size
        self.gravity = 0
        self.gravity_range = 0
        self.world_x, self.world_y = x, y
        self.is_mining = False
        self.mine_rate = 20
        self.mine_range = 90
        self.collision_damage = 15
        self.total_mineable = 100 
        self.ore_remaining = self.total_mineable 

        self.image = utils.load_sprite_variant(ASTEROID_SPRITES)
        if self.image is not None:
            diam = self.size * 2
            self.image = pygame.transform.scale(self.image, (diam, diam))
            self.mask = utils.create_mask_from_img(self.image)
            self.width, self.height = self.image.get_size()
            self.radius = max(self.width, self.height) / 2
        else:
            self.mask = mask

    def get_mask(self):
        return self.mask

    def draw(self, screen, camera):
        screen_pos = camera.apply((self.world_x, self.world_y))
        if self.image is not None:
            rect = self.image.get_rect(center=screen_pos)
            screen.blit(self.image, rect)
        if self.is_mining:
            pygame.draw.circle(screen, (255, 220, 50), screen_pos, self.size + 6, 2)