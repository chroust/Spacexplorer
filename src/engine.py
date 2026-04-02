import pygame
import random
import entities
import math

class Camera:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.x, self.y = 0, 0
        self.target = None

    def follow(self, target):
        self.target = target

    def update(self):
        if self.target:
            self.x, self.y = self.target.world_x, self.target.world_y

    def apply(self, world_pos):
        wx, wy = world_pos
        sx = wx - self.x + self.width // 2
        sy = wy - self.y + self.height // 2
        return sx, sy

class Background:
    def __init__(self, image, win_w, win_h):
        self.image = image
        self.width, self.height = image.get_width(), image.get_height()
        self.win_w, self.win_h = win_w, win_h

    def draw(self, screen, camera):
        offset_x = -camera.x % self.width
        offset_y = -camera.y % self.height
        for x in range(-1, self.win_w // self.width + 2):
            for y in range(-1, self.win_h // self.height + 2):
                screen.blit(self.image, (x * self.width + offset_x, y * self.height + offset_y))

class Minimap:
    def __init__(self, width, height, ship_img):
        minimap_scale = 0.15
        self.minimap_height = height * minimap_scale
        self.minimap_width = width * minimap_scale
        self.pos_x, self.pos_y = 15, 15
        self.zoom = 0.05
        self.ship_img = pygame.transform.scale(ship_img, (9, 15))

    def draw(self, screen, world_instance, player):
        pygame.draw.rect(screen, (20, 20, 20), (15 ,15, self.minimap_width, self.minimap_height))

        minimap_center_x = self.pos_x + self.minimap_width // 2
        minimap_center_y = self.pos_y + self.minimap_height // 2

        for object_list in world_instance.generated_chunks.values():
            for obj in object_list:
                #pos realtive to player
                rel_x = (obj.world_x - player.world_x) * self.zoom
                rel_y = (obj.world_y - player.world_y) * self.zoom

                minimap_x = minimap_center_x + rel_x
                minimap_y = minimap_center_y + rel_y

                if (self.pos_x < minimap_x < self.pos_x + self.minimap_width and 
                    self.pos_y < minimap_y < self.pos_y + self.minimap_height):
                    if obj.type == "dfSpaceObject":
                        color = (0, 255, 0)  # green
                    elif obj.type == "planet":
                        color = (0, 100, 255)  # blue
                    elif obj.type == "asteroid":
                        color = (168, 104, 0)  # brown
                    else:
                        color = (255, 255, 255)  # white for unknown
                    pygame.draw.circle(screen, color, (int(minimap_x), int(minimap_y)), max(1, obj.size * self.zoom))

        rotated_ship = pygame.transform.rotate(self.ship_img, -player.angle - 90)
        ship_rect = rotated_ship.get_rect(center=(minimap_center_x, minimap_center_y))
        screen.blit(rotated_ship, ship_rect)


class WorldManager:
    def __init__(self, chunk_size, seed, object_types):
        self.chunk_size = chunk_size
        self.generated_chunks = {}
        self.world_seed = seed
        self.object_types = object_types

    def get_chunk_coords(self, wx, wy):
        return int(wx // self.chunk_size), int(wy // self.chunk_size)

    def generate_chunk(self, cx, cy):
        if (cx, cy) in self.generated_chunks: return
        random.seed(f"{self.world_seed}_{cx}_{cy}")
        objects = []
        for _ in range(3):
            if random.random() < 0.15:  # 15% sance (3 pokusy, realna sance je trochu mensi pac kdyby se mel spawnout v jinem objektu tak ho proste nespawnu}
                obj_x = cx * self.chunk_size + random.randint(0, self.chunk_size)
                obj_y = cy * self.chunk_size + random.randint(0, self.chunk_size)
                rand = random.random()
                cumulative = 0      # vyber space objekt na zaklade sanci
                for obj_class, prob in self.object_types:
                    cumulative += prob
                    if rand < cumulative:
                        new_obj = obj_class(obj_x, obj_y) 
                        overlaps = False
                        for existing_obj in objects:
                            dx = new_obj.world_x - existing_obj.world_x
                            dy = new_obj.world_y - existing_obj.world_y
                            distance = math.sqrt(dx**2 + dy**2)
                            if distance < (new_obj.size + existing_obj.size):
                                overlaps = True
                                break
                        if not overlaps:
                            objects.append(new_obj)
                        break
        self.generated_chunks[(cx, cy)] = objects

    def update(self, player_x, player_y):
        cx, cy = self.get_chunk_coords(player_x, player_y)
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                self.generate_chunk(x, y)

    def draw(self, screen, camera):
        cx, cy = self.get_chunk_coords(camera.x, camera.y)
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                if (x, y) in self.generated_chunks:
                    for obj in self.generated_chunks[(x, y)]:
                        obj.draw(screen, camera)


class Gravity:
    def __init__(self, strenght):
        self.strenght = strenght
    
    def apply_to_player(self, gravity_object, player):
        dist_x = gravity_object.world_x - player.world_x
        dist_y = gravity_object.world_y - player.world_y
        distance = math.sqrt(dist_x**2 + dist_y**2)
        
        if distance < gravity_object.gravity_range:
            if distance > 0:
                dir_x = dist_x / distance
                dir_y = dist_y / distance
                
                force = gravity_object.gravity / max(1, distance * 0.01)
                
                player.vx += dir_x * force * 0.01
                player.vy += dir_y * force * 0.01

class CollisionChecker:
    def __init__(self):
        self.collision_pairs = []
    
    def check_collision(self, sprite1, sprite2):
        if sprite1.mask is None or sprite2.mask is None:
            return False

        offset_x = int(sprite1.world_x - sprite2.world_x)
        offset_y = int(sprite1.world_y - sprite2.world_y)

        collision_point = sprite1.mask.overlap(sprite2.mask, (offset_x, offset_y))
        
        if collision_point is not None:
            self.collision_pairs.append((sprite1, sprite2))
            return True
        
        return False
    
    def get_collisions(self):
        pairs = self.collision_pairs.copy()
        self.collision_pairs.clear()
        return pairs
    
    # if collision_checker.check_collision(player, obj):
    #     print(f"Player hit {obj.type}")
    #
    #     if obj.type = "objekt kterej si vyberu":
    #       player.nejaka_funkce()   "napr uber hp"
