import math
import pygame
import json
import collections
from pygame.math import Vector2
from src.bubble import Bubble
from src.shooter import Shooter
from src.bubblemap import BubbleMap
from src.hexamaplib.hex_map import HexMap
from src.constants import *
from pygame.locals import *


class Playfield:

    def __init__(self, map_file_path, cell_size):
        """
        Renders a background and gameboard surface.

        :param surface_size: Size to use for the gameboard surface
        :type surface_size: Tuple (int, int)
        :param cell_size: Size to use for HexMap cell size
        :type cell_size: Tuple(int, int)
        """

        self.colorkey = 'WHITE'

        self.cell_size = cell_size
        self.cell_radius = int(cell_size[0] - 2) # this is a magic number, we'll get a better radius method in optimization

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bubble_map = BubbleMap()  # i think i need a new class here
        self.active_bubble = pygame.sprite.GroupSingle()
        self.next_bubble = pygame.sprite.GroupSingle()
        self.disloc_bubbles = pygame.sprite.Group()


        self.load_map(map_file_path)

    def update(self):
        self.image.fill(pygame.Color(self.colorkey))

        # debug
        if DEBUG:
            self.image.blit(self.dbgsurf, (0, 0))

        self.all_sprites.update()

        if self.active_bubble:
            self.process_collision()

        # update and paint everything
        self.all_sprites.draw(self.image)
        self.shooter.draw(self.image)


    def process_collision(self):
        mv = self.active_bubble.sprite

        # check for boundary collision and bounce
        if mv.rect.top < 0:
            mv.bounce(Vector2(1, 0))
            return
        elif mv.rect.left < 0 or mv.rect.right > self.rect.width:
            mv.bounce(Vector2(0, 1))
            return

        collision_list = pygame.sprite.spritecollide(mv, self.bubble_map, False)

        if collision_list:
            # keep going until circle collision
            for spr in collision_list:
                if pygame.sprite.collide_circle(mv, spr):
                    # the idea here is to slow down, find the direction to the nearest sprite,
                    # and move the sprite until it touches at least two others
                    mv.set_position(mv.grid_address, mv.rect.clamp(self.rect).center)
                    mv_cur_address = self.hexmap.get_celladdressbypixel(mv.rect.center)

                    if DEBUG:
                        print("I think I'm in cell {0}.".format(mv_cur_address))

                    mv.grid_address = mv_cur_address
                    dest_cell = self.hexmap.board.get(mv.grid_address)

                    mv.set_velocity(0)
                    mv.set_position(dest_cell.axialpos, dest_cell.get_pixelpos())

                    # move the active bubble to the map
                    self.bubble_map.add(mv)
                    self.active_bubble.remove(mv)

                    return

                continue


    def load_map(self, filepath):
        try:
            map_toplevel = json.load(open(filepath, 'r'))
            map_width = map_toplevel['width']
            map_height = map_toplevel['height']
            map_dict = map_toplevel['map']

        except:
            raise SystemExit('Unable to read file located at {0}.'.format(filepath))

        try:
            # reset affected properties
            #debug
            if DEBUG:
                print("Loading map...")

            self.image = pygame.Surface((map_width, map_height)).convert()
            self.area_params = self.image.get_size()
            self.rect = self.image.get_rect()
            self.hexmap = HexMap(self.area_params, self.cell_size, hex_orientation='pointy')

            # shooter sprite
            # shooter_pos = self.rect.midbottom
            self.shooter = Shooter((0,0), self.all_sprites)
            self.shooter.rect.midbottom = (self.rect.midbottom[0], self.rect.midbottom[1] - 20)

            # debug
            if DEBUG:
                print("Playfield dimensions: {0}".format(self.area_params))
                self.dbgsurf = pygame.Surface(self.area_params)
                self.dbgsurf.fill(pygame.Color(self.colorkey))
                self.dbgsurf.convert()
                for cell in self.hexmap.board.values():
                    cell.paint(self.dbgsurf, color="grey")

            for address in map_dict:
                addr = address.split(", ")
                addr = (int(addr[0]), int(addr[1]))
                self.bubble_map.add(
                    # this is test code for now, just drawing bubbles with primitives
                    # later, the ADDRESS : TYPE json approach will be used to decide which sprite
                    # graphic to load and what special properties (if any) the bubble might have
                    Bubble(
                        addr,                                        # adress
                        self.hexmap.board.get(addr).get_pixelpos(),  # pixelpos
                        self.cell_radius,                            # radius
                        map_dict.get(address),                       # fill_color
                        'BLACK',                                     # stroke_color
                        180,                                         # angle
                        0,                                           # velocity
                        (self.bubble_map, self.all_sprites)          # *groups
                    )
                )

            self.all_sprites.add(self.bubble_map)

        except:
            raise
