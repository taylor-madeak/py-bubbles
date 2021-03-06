import math
import pygame
import json
from random import Random
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

        self.image = None
        self.background = None
        self.rect = None
        self.area_params = None
        self.hexmap = None
        self.shooter = None
        self.dbgsurf = None

        self.bg_color = (255, 255, 255, 150)

        self.cell_size = cell_size
        self.cell_radius = int(cell_size[0] - 2)  # this is a magic number just to accommodate drawn sprites

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bubble_map = BubbleMap()  # i think i need a new class here
        self.active_bubble = pygame.sprite.GroupSingle()
        self.next_bubble = pygame.sprite.GroupSingle()
        self.disloc_bubbles = pygame.sprite.Group()

        # gamey stuff
        self.load_map(map_file_path)
        self.image.blit(self.background, self.rect.topleft)

    def update(self):
        self.image.fill(pygame.Color(*self.bg_color))

        # debug
        if DEBUG:
            self.image.blit(self.dbgsurf, self.rect.topleft)

        # self.all_sprites.clear(self.image, self.background)
        self.all_sprites.update()
        if self.shooter.next.sprite:
            self.all_sprites.add(self.shooter.next.sprite)

        if self.active_bubble.sprite:
            self.process_collision()

        # update and paint everything
        self.all_sprites.draw(self.image)
        self.shooter.draw(self.image)

    def process_collision(self):
        mv = self.active_bubble.sprite

        # check for boundary collision and bounce
        if mv.rect.top < 0:
            #TODO: make bubbles stick to top
            mv.bounce(Vector2(1, 0))
            return
        elif mv.rect.left < 0 or mv.rect.right > self.rect.width:
            mv.bounce(Vector2(0, 1))
            return
        elif mv.rect.top > self.rect.bottom:
            mv.kill()
            return

        collision_list = pygame.sprite.spritecollide(mv, self.bubble_map, False)

        if collision_list:
            # keep going until circle collision
            for spr in collision_list:
                if pygame.sprite.collide_circle(mv, spr):
                    new_pos = mv.rect.clamp(self.rect).center
                    mv.set_position(
                        self._validate_axial_addr(
                            self.hexmap.get_celladdressbypixel(new_pos),
                            self._get_shiftdir(mv)
                        ),
                        new_pos
                    )

                    dest_cell = self.hexmap.board.get(mv.grid_address)

                    mv.set_velocity(0)
                    mv.set_position(dest_cell.axialpos, dest_cell.get_pixelpos())

                    # move the active bubble to the map
                    self.bubble_map.add(mv)
                    self.active_bubble.remove(mv)

                    # testing floodfill
                    matches = self._floodfill(mv, pygame.sprite.Group())
                    if len(matches) >= 3:
                        for sprite in matches:
                            sprite.kill()
                            self.bubble_map.remove(sprite)

                    return

                continue

    def _floodfill(self, sprite, spritegroup):
        """
        Returns a group of touching sprites whose type_property match.

        :type spritegroup: pygame.sprite.Group
        :type sprite: Bubble
        :return: pygame.sprite.Group
        """

        nbr_bubble_addr = [addr for addr in self.hexmap.hex_allneighbors(sprite.grid_address) if addr in self.bubble_map.sprite_dict_by_address.keys()]

        for ax in nbr_bubble_addr:
            b = self.bubble_map.get(ax)
            if b.type_property == sprite.type_property and b not in spritegroup:
                spritegroup.add(b)
                sprite = b
                self._floodfill(sprite, spritegroup)

        return spritegroup

    def _validate_axial_addr(self, axial_addr, shift):
        """
        Validates a Bubble axial address is in range and corrects by shifting left
        or right in the row.  This is intended to correct situations where the bubble
        stops in a map void.
        :param axial_addr: tuple
        :param shift: int
        :return:
        """
        c = 0

        while axial_addr not in self.hexmap.board.keys():
            axial_addr = (axial_addr[0] + shift, axial_addr[1])

            # infinite loops are bad, mmkay?
            assert c < 2, f"Maximum iteration count {c} reached."
            c += 1

        return axial_addr

    def _get_shiftdir(self, sprite):
        """
        Returns +1 or -1 depending on which side of playfield centery the sprite is.
        :param sprite: pygame.sprite.Sprite
        :return: Boolean
        """
        if self.rect.centery < sprite.rect.centery:
            return 1

        return -1

    def load_map(self, filepath):
        try:
            map_toplevel = json.load(open(filepath, 'r'))
            map_width = map_toplevel['width']
            map_height = map_toplevel['height']
            map_dict = map_toplevel['map']

        except Exception:
            raise IOError('Unable to read file located at {0}.'.format(filepath))

        try:
            # reset affected properties
            # debug
            if DEBUG:
                print("Loading map...")

            self.image = pygame.Surface((map_width, map_height)).convert_alpha()
            self.background = pygame.Surface((map_width, map_height)).convert_alpha()
            self.background.fill(pygame.Color(*self.bg_color))
            self.area_params = self.image.get_size()
            self.rect = self.image.get_rect()
            self.hexmap = HexMap(self.area_params, self.cell_size, hex_orientation='pointy')

            # shooter sprite
            # shooter_pos = self.rect.midbottom
            self.shooter = Shooter(
                (0, 0),
                (-5, 15),
                self.hexmap.get_pixeladdressbycell((-5, 15)),
                self.cell_radius,
                self.bubble_map,
                self.all_sprites
            )
            self.shooter.rect.midbottom = (self.rect.midbottom[0], self.rect.midbottom[1] - 20)

            # debug
            if DEBUG:
                print("Playfield dimensions: {0}".format(self.area_params))
                self.dbgsurf = pygame.Surface(self.area_params)
                self.dbgsurf.fill(pygame.Color(self.bg_color))
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
