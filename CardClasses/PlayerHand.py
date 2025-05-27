import pygame
import math
from CardClasses.PokerCard import PokerCard
from CardClasses.CollectedCards import CollectedCards

class PlayerHand(pygame.sprite.LayeredUpdates):
    def __init__(self, center: tuple[int, int], angle:int, radius: int, cards: list[PokerCard]) -> None:
        super().__init__()
        self.center = center
        self.angle = angle
        self.radius = radius
        self.cards = cards

    def add_cards(self, card_list: list[PokerCard]) -> None:
        """
        Adds the cards in a fan-shaped pattern to the hand
        returns None
        """
        try:
            rotation_amplitude = (len(card_list) - 1) * 10
            rotation_step:float = rotation_amplitude / (len(card_list) - 1)
        except ZeroDivisionError:
            rotation_amplitude = 0
            rotation_step = 0
        rotation:float = self.angle + rotation_amplitude / 2
        
        for card in card_list:
            # calculate where along the circle with r = radius the card is located
            center_x = self.center[0] - self.radius * math.sin(math.radians(rotation))
            center_y = self.center[1] - self.radius * math.cos(math.radians(rotation))
            
            # rotate the card by rotation and place at P(center_x, center_y)
            card.rotate_and_move(rotation, (center_x,center_y))
            card.location = card.rect.center
            card.rotation = rotation
            rotation -= rotation_step
            
            # add card to group
            self.add(card)
        
    def edit_masks(self):
        cards = self.sprites()
        for index, card in enumerate(cards):
            for other_card in cards[index+1:]:
                pos_card = card.rect.topleft
                pos_other = other_card.rect.topleft
                offset = (pos_other[0] - pos_card[0], pos_other[1] - pos_card[1])
                card.mask.erase(other_card.mask, offset)
    
    def update_auction(self):
        for card in self.sprites():
            card.update_auction()
            

    def update_card_sort(self, mouse1_state: bool, collected_cards: CollectedCards):
        for card in self.sprites():
            killed = card.update_card_sort(mouse1_state)
            if killed:
                collected_cards.add_cards([card])
                cards = self.sprites()
                self.empty()
                self.add_cards(cards)

    def set_unmovable(self):
        for card in self.sprites():
            card.mobile = False
    
    def set_movable(self):
        for card in self.sprites():
            card.mobile = True
        
