import pygame
import os

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")

def load_image(name):
    return pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()

def create_mask_from_img(surface):
    return pygame.mask.from_surface(surface)

def load_image_with_mask(name):
    image = load_image(name)
    mask = create_mask_from_img(image)
    return image, mask