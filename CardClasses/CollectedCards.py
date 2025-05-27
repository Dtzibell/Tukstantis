from CardClasses.PokerCard import PokerCard
import pygame
class CollectedCards(pygame.sprite.LayeredUpdates):
    def __init__(self, center_coords: tuple[float,float], rotation: int):
        super().__init__()
        self.center = center_coords
        self.top_layer = 0
        self.rotation = rotation
    
    def add_cards(self, cards: PokerCard|list[PokerCard]):
        for card in cards:
            card.rotate_and_move(self.rotation, self.center)
            self.add(card)
            self.change_layer(card, self.top_layer)
            self.top_layer += 1

    def update(self, mouse1_state: bool, player_dict: dict):
        try:
            top_card = self.get_top_sprite()
            top_card.update_collected(mouse1_state, player_dict)
        except IndexError:
            pass