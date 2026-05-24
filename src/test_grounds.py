import pygame
import math
import utils
import engine
import entities
from main import WIN_WIDTH, WIN_HEIGHT

BORDER_WIDTH = 1260
BORDER_HEIGHT = 700
set_x = 300
set_y = 0
rotate = 90

class Border:
    def __init__(self, BORDER_WIDTH, BORDER_HEIGHT):
        self.width = BORDER_WIDTH
        self.height = BORDER_HEIGHT

    def draw(self, screen, camera):
        world_left = -self.width // 2
        world_top = -self.height // 2
        screen_left, screen_top = camera.apply((world_left, world_top))
        pygame.draw.rect(screen, (150, 0, 0), (screen_left, screen_top, self.width, self.height), 5)

    def touch(self, player):
        ship_w = player.image.get_width()
        ship_h = player.image.get_height()
        
        limit_x = self.width // 2
        limit_y = self.height // 2

        if player.world_x >= limit_x - ship_w // 2:
            player.world_x = limit_x - ship_w // 2
            player.vx = -0.5

        elif player.world_x <= -limit_x + ship_w // 2:
            player.world_x = -limit_x + ship_w // 2
            player.vx = 0.5

        if player.world_y >= limit_y - ship_h // 2:
            player.world_y = limit_y - ship_h // 2
            player.vy = -0.5

        elif player.world_y <= -limit_y + ship_h // 2:
            player.world_y = -limit_y + ship_h // 2
            player.vy = 0.5
        
class Configure:
    def __init__(self, player):
        player.world_x = set_x
        player.world_y = set_y


class TypeDisplay:
    def __init__(self, x=BORDER_WIDTH//2, y=10):
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, 32)
        self.current_type = None
        self.text_surface = None
        self.text_rect = None

    def update(self, object_type):
        self.current_type = object_type
        self.text_surface = self.font.render(f"Selected: {object_type.__name__}", True, (0, 255, 0))
        self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        if self.text_surface:
            background = pygame.Surface((self.text_rect.width + 10, self.text_rect.height + 6))
            background.set_alpha(150)
            background.fill((0, 0, 0))
            screen.blit(background, (self.text_rect.left - 5, self.text_rect.top - 3))
            screen.blit(self.text_surface, self.text_rect)


def run_test_grounds():
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    ship_img, ship_mask = utils.load_image_with_mask("spaceship.png")
    player = entities.Ship(ship_img, ship_mask)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player)

    world = engine.WorldManager(2000, "seedyseed", [])
    minimap = engine.Minimap(WIN_WIDTH, WIN_HEIGHT, ship_img)
    collision_checker = engine.CollisionChecker()

    config = Configure(player)
    border = Border(BORDER_WIDTH, BORDER_HEIGHT)
    type_display = TypeDisplay()
    gravity = engine.Gravity(1.0)

    object_types = [
        entities.dfSpaceObject,
        entities.planet,
        entities.asteriod,
        entities.EnemyShip,
        entities.BlackHole
    ]
    current_type_index = 0
    spawned_objects = []
    type_display.update(object_types[current_type_index])
    game_time = 0.0

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    current_type_index = (current_type_index + 1) % len(object_types)
                    type_display.update(object_types[current_type_index])
                    print(f"Selected object: {object_types[current_type_index].__name__}")

                elif event.key == pygame.K_s:
                    obj_class = object_types[current_type_index]
                    spawn_x = player.world_x + 150
                    spawn_y = player.world_y
                    new_obj = obj_class(spawn_x, spawn_y)
                    spawned_objects.append(new_obj)
                    print(f"Spawned {obj_class.__name__} at ({spawn_x}, {spawn_y})")

                elif event.key == pygame.K_c:
                    spawned_objects.clear()
                    print("Cleared all spawned objects")

                elif event.key == pygame.K_r:
                    config = Configure(player)
                    player.vx = 0
                    player.vy = 0
                    print("Player reset to test center")

        keys = pygame.key.get_pressed()
        player.update(keys, None, delta_time)
        game_time += delta_time
        camera.update()

        for obj in spawned_objects:
            if getattr(obj, 'type', None) == "enemy":
                obj.update(player, delta_time, game_time)
            if getattr(obj, 'type', None) == "blackhole":
                pass
            gravity.apply_to_player(obj, player)

        world.active_enemies = [e for e in spawned_objects if getattr(e, 'type', None) == "enemy" and e.active]

        for obj in spawned_objects:
            if getattr(obj, 'type', None) == "enemy" and not obj.active:
                continue
            collision_checker.check_collision(player, obj)

        collisions = collision_checker.get_collisions()
        for player_obj, other_obj in collisions:
            if other_obj.type in ("planet", "asteroid", "enemy", "blackhole"):
                if player.take_damage(other_obj.collision_damage):
                    dx = player.world_x - other_obj.world_x
                    dy = player.world_y - other_obj.world_y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        bounce_speed = 5
                        player.vx = (dx / dist) * bounce_speed
                        player.vy = (dy / dist) * bounce_speed
                    else:
                        player.vx *= -1.5
                        player.vy *= -1.5
                if other_obj.type == "enemy":
                    other_obj.take_damage(1)

        screen.fill((0, 0, 0))
        for obj in spawned_objects:
            if getattr(obj, 'type', None) == "enemy" and not obj.active:
                continue
            obj.draw(screen, camera)

        player.draw(screen, camera)
        border.draw(screen, camera)
        border.touch(player)
        type_display.draw(screen)

        font = pygame.font.Font(None, 24)
        instructions = [
            "T - cycle object type",
            "S - spawn selected object near player",
            "C - clear objects",
            "R - reset player position"
        ]
        for idx, line in enumerate(instructions):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (10, 10 + idx * 22))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_test_grounds()