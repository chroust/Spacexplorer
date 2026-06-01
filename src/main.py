import pygame
import math
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
    upgrade_menu = menu.UpgradeMenu(WIN_WIDTH, WIN_HEIGHT)

    state = 'start_menu'
    game_objects = None

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0

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

            elif state == 'upgrade_menu':
                result = upgrade_menu.handle_input(event, game_objects['player'])
                if result == 'close':
                    state = 'game'

            elif state == 'game':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = 'pause_menu'
                    pause_menu.reset_selection()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    state = 'upgrade_menu'

        if state == 'start_menu':
            start_menu.draw(screen)

        elif state == 'pause_menu':
            pause_menu.draw(screen)

        elif state == 'upgrade_menu' and game_objects:
            draw_game(screen, game_objects)
            upgrade_menu.update(delta_time)
            upgrade_menu.draw(screen, game_objects['player'])

        elif state == 'game' and game_objects:
            update_game(game_objects, delta_time)
            if game_objects['player'].fuel <= 0 or game_objects['player'].health <= 0:
                state = 'start_menu'
                game_objects = None
            else:
                draw_game(screen, game_objects)

        pygame.display.flip()

    pygame.quit()

def initialize_game():
    ship_img, ship_mask = utils.load_image_with_mask("spaceship_lightened.png")
    bg_img = utils.load_image("starfield.png")

    player = entities.Ship(ship_img, ship_mask)
    camera = engine.Camera(WIN_WIDTH, WIN_HEIGHT)
    camera.follow(player)
    
    background = engine.Background(bg_img, WIN_WIDTH, WIN_HEIGHT)
    object_types = [
        (entities.dfSpaceObject, 0.30),  # 30%
        (entities.planet, 0.18),          # 18%
        (entities.asteriod, 0.23),       # 23%
        (entities.EnemyShip, 0.22),      # 22%
        (entities.BlackHole, 0.07)        # 7%
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
        'collision_checker': collision_checker,
        'game_time': 0.0
    }

def update_game(game_objects, delta_time):
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

    player.update(keys, unpress, delta_time)
    game_objects['game_time'] += delta_time
    camera.update()
    world.update(player.world_x, player.world_y)

    laser_level    = player.upgrade_levels.get("mining_laser", 0)
    mining_multiplier    = 1.0 + laser_level * 0.5
    
    refuel_rate = 100
    refuel_range = 50  # pocita se to od stredu objektu takze je to vlastne podobne velky jako ten objekt rn
    player.is_mining = False

    world.active_enemies = [e for e in world.active_enemies if e.active]

    for enemy in world.active_enemies:
        enemy.update(player, delta_time, game_objects['game_time'])
        collision_checker.check_collision(player, enemy)

    for object_list in world.generated_chunks.values():
        for obj in object_list:
            if obj.type == "enemy":
                continue
            
            # Update blackhole animation
            if obj.type == "blackhole" and obj.animation:
                obj.animation.update(delta_time)

            gravity.apply_to_player(obj, player)
            collision_checker.check_collision(player, obj)
            
            if obj.type == "dfSpaceObject":
                dx = obj.world_x - player.world_x
                dy = obj.world_y - player.world_y
                distance = math.sqrt(dx**2 + dy**2)
                if distance <= refuel_range:
                    player.refill_fuel(refuel_rate * delta_time)
                    obj.highlighted = True
                else:
                    obj.highlighted = False

            elif hasattr(obj, 'mine_rate') and obj.mine_rate > 0:
                dx = obj.world_x - player.world_x
                dy = obj.world_y - player.world_y
                if math.sqrt(dx**2 + dy**2) <= obj.mine_range:
                    player.credits += obj.mine_rate * mining_multiplier * delta_time
                    player.is_mining = True
                    obj.is_mining = True
                else:
                    obj.is_mining = False

    for enemy in world.active_enemies:
        if not enemy.active:
            continue
        for target_list in world.generated_chunks.values():
            for target in target_list:
                if target is enemy or target.type not in ("planet", "asteroid"):
                    continue
                dx = enemy.world_x - target.world_x
                dy = enemy.world_y - target.world_y
                if dx * dx + dy * dy <= (enemy.radius + target.radius) ** 2:
                    enemy.take_damage(1)
                    break
            if not enemy.active:
                break

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
    
    fuel_ratio = player.fuel / player.fuel_max
    bar_width = 200
    bar_height = 20
    bar_x = WIN_WIDTH - bar_width - 20
    bar_y = 20
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # Background img
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * fuel_ratio, bar_height))  # Fuel indicator
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)  # Border
    
    font = pygame.font.SysFont(None, 24)
    fuel_text = f"Fuel: {int(player.fuel)}/{int(player.fuel_max)}"
    text_surface = font.render(fuel_text, True, (255, 255, 255))
    screen.blit(text_surface, (bar_x, bar_y + bar_height + 5))

    credits_text = f"Credits: {int(player.credits)}"
    screen.blit(font.render(credits_text, True, (255, 215, 0)), (bar_x, bar_y + bar_height + 25))

    health_ratio = player.health / player.health_max
    health_width = 200
    health_height = 12
    health_x = bar_x
    health_y = bar_y + bar_height + 50
    pygame.draw.rect(screen, (80, 80, 80), (health_x, health_y, health_width, health_height))
    pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width * health_ratio, health_height))
    pygame.draw.rect(screen, (255, 255, 255), (health_x, health_y, health_width, health_height), 2)
    screen.blit(font.render(f"Health: {int(player.health)}/{int(player.health_max)}", True, (255, 255, 255)), (health_x, health_y + health_height + 3))

    if player.is_mining:
        mining_surf = pygame.font.SysFont(None, 30).render("Mining...", True, (255, 220, 50))
        screen.blit(mining_surf, (WIN_WIDTH // 2 - mining_surf.get_width() // 2, 20))

    hint = font.render("TAB - Upgrade Shop", True, (100, 100, 130))
    screen.blit(hint, (WIN_WIDTH - hint.get_width() - 20, WIN_HEIGHT - 30))


if __name__ == '__main__':
    main()