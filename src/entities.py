import pygame
import math
import random
import utils

PLANET_SPRITES: list[str] = [
    "planets/red_planet.png",
    "planets/purple_planet.png",
    "planets/purple_green_planet.png"
]
ASTEROID_SPRITES: list[str] = [
    "asteroids/asteroid.png",
    "asteroids/ice_asteroid.png"
]



class Ship:
    # Spritesheet: 180×75 px — 5 cols × 1 row — 36×75 px per frame
    # Frame 0: engine off (idle pose, no flame)
    # Frames 1-4: thrust animation, increasing flame intensity
    FRAME_W, FRAME_H = 36, 75

    def __init__(self, image: pygame.Surface, mask: pygame.mask.Mask,
                 spritesheet_name: str = "spaceship_spritesheet.png",
                 frame_duration: float = 0.08) -> None:
        self.world_x, self.world_y = 0.0, 0.0
        self.vx, self.vy = 0.0, 0.0
        self.angle = -90.0
        self.rotation_speed = 4
        self.target_angle = -90.0
        self.thrust = 0.25
        self.friction = 0.98
        self.image = image
        self.mask = mask
        self.radius = max(image.get_width(), image.get_height()) / 2
        self.fuel_max = 1000.0
        self.fuel = self.fuel_max
        self.fuel_consumption = 30.0
        self.health_max = 100.0
        self.health = self.health_max
        self.damage_cooldown = 0.6
        self.damage_timer = 0.0
        self.credits = 0.0
        self.upgrade_levels: dict = {}
        self.is_mining = False
        self.is_moving = False

        frames = utils.load_spritesheet(spritesheet_name, self.FRAME_W, self.FRAME_H)
        self.animation = utils.AnimationController(
            frames,
            frame_duration=frame_duration,
            loop=True,
            start_frame=0,
            loop_start_frame=1,
        )

    def update(self, keys, unpress, delta_time: float) -> None:
        if keys[pygame.K_a]:
            self.target_angle -= self.rotation_speed
        if keys[pygame.K_d]:
            self.target_angle += self.rotation_speed
        self.angle += 0.035 * (self.target_angle - self.angle)

        self.is_moving = keys[pygame.K_w] and self.fuel > 0
        if self.is_moving:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.thrust
            self.vy += math.sin(rad) * self.thrust
            self.fuel -= self.fuel_consumption * delta_time

            if not self.animation.is_playing:
                self.animation.current_frame = 1
            self.animation.play()
        else:
            self.animation.stop()
            self.animation.reset()

        self.world_x += self.vx
        self.world_y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction
        self.damage_timer = max(self.damage_timer - delta_time, 0.0)
        self.animation.update(delta_time)

    def refill_fuel(self, amount: float) -> None:
        self.fuel = min(self.fuel + amount, self.fuel_max)

    def take_damage(self, amount: float) -> bool:
        if self.damage_timer > 0:
            return False
        self.health = max(self.health - amount, 0)
        self.damage_timer = self.damage_cooldown
        return True

    def draw(self, screen: pygame.Surface, camera) -> None:
        frame = self.animation.get_current_frame()
        draw_image = frame if frame is not None else self.image
        rotated = pygame.transform.rotate(draw_image, -self.angle - 90)
        screen_pos = camera.apply((self.world_x, self.world_y))
        screen.blit(rotated, rotated.get_rect(center=screen_pos))



class dfSpaceObject:
    def __init__(self, x: float, y: float, mask=None) -> None:
        self.type = "dfSpaceObject"
        self.size = 20
        self.radius = self.size
        self.gravity = 0.5
        self.gravity_range = 500
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.highlighted = False
        self.mine_rate = 0
        self.mine_range = 0
        self.collision_damage = 0

    def draw(self, screen: pygame.Surface, camera) -> None:
        pos = camera.apply((self.world_x, self.world_y))
        color = (255, 255, 0) if self.highlighted else (0, 255, 0)
        if self.highlighted:
            pygame.draw.circle(screen, (255, 255, 0), pos, self.size + 5, 2)
        pygame.draw.circle(screen, color, pos, self.size)



class EnemyShip:
    def __init__(self, x: float, y: float, mask=None) -> None:
        self.type = "enemy"
        self.size = 30
        self.radius = self.size
        self.gravity = 0
        self.gravity_range = 0
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.vx, self.vy = 0.0, 0.0
        self.angle = 0.0
        self.target_angle = 0.0
        self.rotation_speed = 3
        self.thrust = 0.18
        self.friction = 0.97
        self.collision_damage = 20
        self.health = 1
        self.active = True
        self.chase_range = 1500
        self.despawn_range = 3500

    def update(self, player, delta_time: float, game_time: float) -> None:
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

    def take_damage(self, amount: float) -> bool:
        if not self.active:
            return False
        self.health = max(self.health - amount, 0)
        if self.health <= 0:
            self.active = False
            return True
        return False

    def draw(self, screen: pygame.Surface, camera) -> None:
        if not self.active:
            return
        pos = camera.apply((self.world_x, self.world_y))
        pygame.draw.circle(screen, (200, 30, 30), pos, self.size)
        pygame.draw.circle(screen, (255, 255, 255), pos, self.size, 2)



class BlackHole:
    # Spritesheet: 600×644 px — 5 cols × 7 rows — 120×92 px per frame — 35 frames
    # Frames 32-34 (last 3) are fully blank padding; end_frame=31 skips them.
    FRAME_W, FRAME_H = 120, 92

    def __init__(self, x: float, y: float, mask=None,
                 spritesheet_name: str = "black_hole_spritesheet.png",
                 frame_duration: float = 0.08) -> None:
        self.type = "blackhole"
        self.size = random.randint(20, 170)
        self.radius = self.size
        self.gravity = 10.0
        self.gravity_range = self.size * 10
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.collision_damage = 9999
        self.is_mining = False

        try:
            frames = utils.load_spritesheet(spritesheet_name, self.FRAME_W, self.FRAME_H)
            self.animation = utils.AnimationController(
                frames,
                frame_duration=frame_duration,
                loop=True,
                end_frame=31,   # Frames 32-34 are blank padding — skip them
            )
            self.animation.play()
        except Exception:
            self.animation = None

    def draw(self, screen: pygame.Surface, camera) -> None:
        pos = camera.apply((self.world_x, self.world_y))
        diam = self.size * 2
        frame = self.animation.get_current_frame() if self.animation else None
        if frame is not None:
            scaled = pygame.transform.scale(frame, (diam, diam))
            screen.blit(scaled, scaled.get_rect(center=pos))
        else:
            pygame.draw.circle(screen, (10, 10, 10), pos, self.size)
            pygame.draw.circle(screen, (120, 0, 180), pos, int(self.size * 0.8), 3)
            pygame.draw.circle(screen, (190, 0, 255), pos, int(self.size * 0.45), 2)



class planet:
    def __init__(self, x: float, y: float, mask=None) -> None:
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

        raw = utils.load_sprite_variant(PLANET_SPRITES)
        if raw is not None:
            diam = self.size * 2
            scaled = pygame.transform.scale(raw, (diam, diam))
            self.image: pygame.Surface | None = pygame.transform.rotate(
                scaled, random.randint(0, 359)
            )
        else:
            self.image = None

    def draw(self, screen: pygame.Surface, camera) -> None:
        pos = camera.apply((self.world_x, self.world_y))
        if self.image is not None:
            screen.blit(self.image, self.image.get_rect(center=pos))
        else:
            pygame.draw.circle(screen, (0, 100, 255), pos, self.size)
        if self.is_mining:
            pygame.draw.circle(screen, (255, 220, 50), pos, self.size + 8, 3)


class asteriod:
    def __init__(self, x: float, y: float, mask=None) -> None:
        self.type = "asteroid"
        self.size = 25
        self.radius = self.size
        self.gravity = 0
        self.gravity_range = 0
        self.world_x, self.world_y = x, y
        self.mask = mask
        self.is_mining = False
        self.mine_rate = 20
        self.mine_range = 90
        self.collision_damage = 15

        raw = utils.load_sprite_variant(ASTEROID_SPRITES)
        if raw is not None:
            diam = self.size * 2
            scaled = pygame.transform.scale(raw, (diam, diam))
            self.image: pygame.Surface | None = pygame.transform.rotate(
                scaled, random.randint(0, 359)
            )
        else:
            self.image = None

    def draw(self, screen: pygame.Surface, camera) -> None:
        pos = camera.apply((self.world_x, self.world_y))
        if self.image is not None:
            screen.blit(self.image, self.image.get_rect(center=pos))
        else:
            pygame.draw.circle(screen, (168, 104, 0), pos, self.size)
        if self.is_mining:
            pygame.draw.circle(screen, (255, 220, 50), pos, self.size + 6, 2)