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
    def __init__(self, BORDER_WIDTH, BORDER_HEIGHT, screen):
        self.width = BORDER_WIDTH
        self.height = BORDER_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 0, 0), (10, 10, self.width, self.height), 5)

    def touch(self, player, BORDER_WIDTH, BORDER_HEIGHT):
        ship_w = player.image.get_width()
        ship_h = player.image.get_height()
        
        limit_x = BORDER_WIDTH // 2
        limit_y = BORDER_HEIGHT // 2

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


def run_test_grounds():
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    ship_img = utils.load_image("spaceship.png")
    player = entities.Ship(ship_img)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    world = engine.WorldManager(2000, "seedyseed", entities.dfSpaceObject)
    minimap = engine.Minimap(WIN_WIDTH, WIN_HEIGHT, ship_img)

    config = Configure(player) 
    border = Border(BORDER_WIDTH, BORDER_HEIGHT, screen)

    # Object spawning
    object_types = [entities.dfSpaceObject, entities.planet]
    current_type_index = 0
    spawned_objects = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:  # Cycle through object types
                    current_type_index = (current_type_index + 1) % len(object_types)
                    print(f"Selected object: {object_types[current_type_index].__name__}")
                elif event.key == pygame.K_s:  # Spawn object
                    obj_class = object_types[current_type_index]
                    if obj_class == entities.dfSpaceObject:
                        new_obj = obj_class(player.world_x + 100, player.world_y, "test")
                    elif obj_class == entities.planet:
                        new_obj = obj_class(player.world_x + 100, player.world_y)
                    spawned_objects.append(new_obj)
                    print(f"Spawned {obj_class.__name__}")
                elif event.key == pygame.K_c:  # Clear spawned objects
                    spawned_objects.clear()
                    print("Cleared all spawned objects")

        clock.tick(60)

        keys = pygame.key.get_pressed()
        player.update(keys, False)  # Assuming unpress not needed here
        screen.fill((0, 0, 0))
        player.draw(screen, camera)

        # Draw spawned objects
        for obj in spawned_objects:
            obj.draw(screen, camera)

        border.draw(screen)
        border.touch(player, BORDER_WIDTH, BORDER_HEIGHT)

        pygame.display.flip()
        clock.tick(180)

    pygame.quit()


if __name__ == "__main__":
    run_test_grounds()