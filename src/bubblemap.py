from pygame.sprite import Group, Sprite
from bubble import Bubble


class BubbleMap(Group):

    def __init__(self, *sprites):
        """

        :type *sprites: bubble.Bubble
        """
        super().__init__(*sprites)

        # internal structure that keeps track of Bubbles by grid address
        self._sprite_dict = dict()

    def add(self, *sprites):
        super().add(*sprites)

        for obj in sprites:
            if obj not in self._sprite_dict:
                self._sprite_dict[obj.grid_address] = obj

    def remove(self, *sprites):
        super().remove(*sprites)

        for obj in sprites:
            if obj in self._sprite_dict:
                del self._sprite_dict[obj.grid_address]

    def empty(self):
        super().empty()
        self._sprite_dict.clear()

    def get(self, address):
        try:
            return self._sprite_dict[address]

        except KeyError:
            return None

    def get_present_types(self):
        """
        Returns a list of unique Bubble types currently present in map.

        :return: List
        """
        result = list()

        for item in self._sprite_dict.values():
            if item.type_property not in result:
                result.append(item.type_property)

        return result
