import pygame
import os

from settings import (
    tile_width,
    tile_height,
    screen_width,
    screen_height,
    tile_interval_x,
    tile_interval_y,
    shelf_width,
    shelf_height,
    window_width,
    img_path,
)

class Tile:
    def __init__(self, suit, value):
        self.ID = None
        self.suit = suit
        self.value = value
        self.overlaping = False  # if the tile been inserted
        self.getImg()
        self.unlock = True

    def createSpecificTile(self, s, v):
        self.suit = s
        self.value = v

    def getImg(self):
        # define the color
        color_dict = {
            "red": (255, 0, 0),
            "green": (100, 190, 70),
            "blue": (51, 204, 225),
            "yellow": (255, 153, 18),
            "black": (0, 0, 0)
        }
        # create tiles type
        suitDict = {1: "red", 2: "green", 3: "blue", 4: "yellow", 5: "black"}
        valueDict = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", \
                     6: "6", 7: "7", 8: "8", 9: "9", 10: "10", \
                     11: "11", 12: "12", 13: "13", 14: "14", 15: "15"}

        global tile_width, tile_height
        # create the size of tile
        tile_surface = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
        tile_surface.fill((0, 0, 0, 0))
        # load the tile background image
        tile_background = pygame.image.load(os.path.join(img_path,'tile.png'))
        tile_background = pygame.transform.scale(tile_background, (tile_width, tile_height))
        tile_surface.blit(tile_background, (0, 0))
        # define font and colour
        font = pygame.font.Font(None, 42)
        font.set_bold(True)
        text_color = color_dict.get(suitDict[self.suit], (0, 0, 0))
        text = font.render(str(valueDict[self.value]), True, text_color)
        text_rect = text.get_rect(center=(tile_width // 2, tile_height // 3))
        # render the tile
        tile_surface.blit(text, text_rect)
        self.tile_img = tile_surface
        return self.tile_img
