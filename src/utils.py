import pygame
import os

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")

def load_image(name):
    return pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()