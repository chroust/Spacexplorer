import pygame
import space

BORDER_WIDTH, BORDER_HEIGHT = 1280, 720

class Border:
    def __init__(self, BORDER_WIDTH, BORDER_HEIGHT):
        ship_img = space.load_image("spaceship.png") 
        player = space.Ship(ship_img)
        current_ship_x = player.world_x
        current_ship_y = player.world_y
        print(player.world_x)


        if current_ship_x == 0:
            pass


def run_test_grounds():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    ship_image = space.load_image("spaceship.png")
    player = space.Ship(ship_image)
    camera = space.Camera(1280, 720)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                unpress = True

        Border(BORDER_WIDTH, BORDER_HEIGHT)

        keys = pygame.key.get_pressed()
        unpress = pygame.key.get_just_released()
        player.update(keys, unpress)
        screen.fill((0, 0, 0))
        player.draw(screen, camera)
        
        pygame.display.flip()
        clock.tick(180)

    pygame.quit()

if __name__ == "__main__":
    run_test_grounds()