import pygame
import main
import utils
import engine
import entities

BORDER_WIDTH, BORDER_HEIGHT = 1260, 700

class Border:
    def __init__(self, BORDER_WIDTH, BORDER_HEIGHT, screen):
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, BORDER_WIDTH, BORDER_HEIGHT), 5)

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
        



def run_test_grounds():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    ship_image = utils.load_image("spaceship.png")
    player = entities.Ship(ship_image)
    camera = engine.Camera(1280, 720)

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

        

        #print(player.world_x, player.world_y)

        keys = pygame.key.get_pressed()
        unpress = pygame.key.get_just_released()
        player.update(keys, unpress)
        screen.fill((0, 0, 0))
        player.draw(screen, camera)
        border = Border(BORDER_WIDTH, BORDER_HEIGHT, screen)
        border.touch(player, BORDER_WIDTH, BORDER_HEIGHT)


        pygame.display.flip()
        clock.tick(180)

    pygame.quit()

if __name__ == "__main__":
    run_test_grounds()