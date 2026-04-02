import pygame
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

    ship_img = utils.load_image("spaceship.png")
    player = entities.Ship(ship_img)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    object_types = [
        # (entities.dfSpaceObject, 0.5),      nechci aby se mi tam nic automaticky spawnovalo, ale mam tu moznost
        # (entities.planet, 0.2),
        # (entities.asteriod, 0.3)
    ]
    world = engine.WorldManager(2000, "seedyseed", object_types)
    minimap = engine.Minimap(WIN_WIDTH, WIN_HEIGHT, ship_img)

    config = Configure(player) 
    border = Border(BORDER_WIDTH, BORDER_HEIGHT)
    type_display = TypeDisplay()
    gravity = engine.Gravity(1.0)

    # Object spawning
    object_types = [entities.dfSpaceObject, entities.planet, entities.asteriod]
    current_type_index = 0
    spawned_objects = []
    type_display.update(object_types[current_type_index])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    current_type_index = (current_type_index + 1) % len(object_types)
                    type_display.update(object_types[current_type_index])
                    print(f"Selected object: {object_types[current_type_index].__name__}")

                elif event.key == pygame.K_s:
                    obj_class = object_types[current_type_index]
                    if obj_class == entities.dfSpaceObject:
                        new_obj = obj_class(0, 0, "test")
                    elif obj_class == entities.planet:
                        new_obj = obj_class(0, 0)
                    elif obj_class == entities.asteriod:
                        new_obj = obj_class(0, 0)
                    spawned_objects.append(new_obj)
                    print(f"Spawned {obj_class.__name__} at border center (0,0)")

                elif event.key == pygame.K_c:
                    spawned_objects.clear()
                    print("Cleared all spawned objects")

        clock.tick(60)

        keys = pygame.key.get_pressed()
        player.update(keys, False)
        
        for obj in spawned_objects:
            gravity.apply_to_player(obj, player)
        
        screen.fill((0, 0, 0))
        player.draw(screen, camera)

        for obj in spawned_objects:
            obj.draw(screen, camera)

        border.draw(screen, camera)
        border.touch(player)
        type_display.draw(screen)

        pygame.display.flip()
        clock.tick(180)

    pygame.quit()


if __name__ == "__main__":
    run_test_grounds()