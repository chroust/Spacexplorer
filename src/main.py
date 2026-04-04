import pygame
import utils
import entities
import engine
import menu

WIN_WIDTH, WIN_HEIGHT = 1280, 720

seed = "seedyseed"


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Space Game")
    clock = pygame.time.Clock()

    start_menu = menu.Menu(WIN_WIDTH, WIN_HEIGHT, "Space Explorer", ['Start Game', 'Quit'])
    pause_menu = menu.Menu(WIN_WIDTH, WIN_HEIGHT, "Paused", ['Resume', 'Restart', 'Quit to Menu', 'Quit Game'])

    state = 'start_menu'
    game_objects = None  # Will hold game objects when initialized

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif state == 'start_menu':
                choice = start_menu.handle_input(event)
                if choice == 'Start Game':
                    state = 'game'
                    game_objects = initialize_game()
                elif choice == 'Quit':
                    running = False
            elif state == 'pause_menu':
                choice = pause_menu.handle_input(event)
                if choice == 'Resume':
                    state = 'game'
                elif choice == 'Restart':
                    game_objects = initialize_game()
                    state = 'game'
                elif choice == 'Quit to Menu':
                    state = 'start_menu'
                    game_objects = None
                elif choice == 'Quit Game':
                    running = False
            elif state == 'game':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = 'pause_menu'
                    pause_menu.reset_selection()

        if state == 'start_menu':
            start_menu.draw(screen)
        elif state == 'pause_menu':
            pause_menu.draw(screen)
        elif state == 'game' and game_objects:
            update_game(game_objects)
            draw_game(screen, game_objects)

        pygame.display.flip()

    pygame.quit()

def initialize_game():
    ship_img, ship_mask = utils.load_image_with_mask("spaceship.png")
    bg_img = utils.load_image("test_bg.jpg")

    player = entities.Ship(ship_img, ship_mask)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player)
    
    background = engine.Background(bg_img, WIN_WIDTH, WIN_HEIGHT)
    object_types = [
        (entities.dfSpaceObject, 0.5),  # 50% chance
        (entities.planet, 0.2),         # 20% chance
        (entities.asteriod, 0.3)        # 30% chance
    ]
    world = engine.WorldManager(2000, seed, object_types)
    minimap = engine.Minimap(WIN_WIDTH, WIN_HEIGHT, ship_img)
    gravity = engine.Gravity(1.0)
    collision_checker = engine.CollisionChecker()

    return {
        'player': player,
        'camera': camera,
        'background': background,
        'world': world,
        'minimap': minimap,
        'gravity': gravity,
        'collision_checker': collision_checker
    }

def update_game(game_objects):
    player = game_objects['player']
    camera = game_objects['camera']
    world = game_objects['world']
    gravity = game_objects['gravity']
    collision_checker = game_objects['collision_checker']

    keys = pygame.key.get_pressed()
    try:
        unpress = pygame.key.get_just_released()
    except AttributeError:
        unpress = None

    player.update(keys, unpress)
    camera.update()
    world.update(player.world_x, player.world_y)
    
    for object_list in world.generated_chunks.values():
        for obj in object_list:
            gravity.apply_to_player(obj, player)
            collision_checker.check_collision(player, obj)

def draw_game(screen, game_objects):
    camera = game_objects['camera']
    background = game_objects['background']
    world = game_objects['world']
    player = game_objects['player']
    minimap = game_objects['minimap']

    screen.fill((0, 0, 0))
    background.draw(screen, camera)
    world.draw(screen, camera)
    player.draw(screen, camera)
    minimap.draw(screen, world, player)


if __name__ == '__main__':
    main()