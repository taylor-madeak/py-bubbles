import pygame


class Bubble:

    def __init__(self, color, size, position, surface) -> None:
        assert isinstance(color, str)
        assert isinstance(size, int)
        assert isinstance(position, tuple)
        assert isinstance(surface, pygame.Surface)

        self.color = color
        self.size = size
        self.pos = position  # set a starting position
        self.__surface = surface  # this is meant to be a private constant

        self.__sprite = pygame.draw.circle(self.__surface, self.color, self.pos, self.size)  # placeholder

    def draw(self):
        self.__surface.blit(self.__sprite, self.__surface)
