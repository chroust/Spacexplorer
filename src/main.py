import pygame
import utils
import entities
import engine

def main():
    pygame.init()
    WIN_WIDTH, WIN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Space Game - Modular Edition")
    clock = pygame.time.Clock()

    ship_img = utils.load_image("spaceship.png")
    bg_img = utils.load_image("test_bg.jpg")

    player = entities.Ship(ship_img)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player) # camera to the player instance
    
    background = engine.Background(bg_img, WIN_WIDTH, WIN_HEIGHT)
    world = engine.WorldManager(2000, "seedyseed", entities.dfSpaceObject)

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

        screen.fill((0, 0, 0))
        background.draw(screen, camera)
        world.draw(screen, camera)
        player.draw(screen, camera)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()