import pygame
import utils
import entities
import engine

WIN_WIDTH, WIN_HEIGHT = 1280, 720

seed = "seedyseed"


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Space Game")
    clock = pygame.time.Clock()

    ship_img = utils.load_image("spaceship.png")
    bg_img = utils.load_image("test_bg.jpg")

    player = entities.Ship(ship_img)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player)
    
    background = engine.Background(bg_img, WIN_WIDTH, WIN_HEIGHT)
    world = engine.WorldManager(2000, seed, entities.dfSpaceObject)
    minimap = engine.Minimap(WIN_WIDTH,WIN_HEIGHT, ship_img)
    gravity = engine.Gravity(1.0)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
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

        screen.fill((0, 0, 0))
        background.draw(screen, camera)
        world.draw(screen, camera)
        player.draw(screen, camera)
        minimap.draw(screen, world, player)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()