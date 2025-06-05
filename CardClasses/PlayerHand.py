import pygame
import math
from CardClasses.PokerCard import PokerCard

class PlayerHand(pygame.sprite.LayeredUpdates):
    def __init__(self, center: tuple[int, int], angle:int) -> None:
        super().__init__()
        self.center: tuple[int,int] = center
        self.angle: int = angle
        self.cards: dict[str, PokerCard] = dict()

    def add_cards(self, card_list: dict[str, PokerCard]) -> None:
        """
        Adds the cards in a fan-shaped pattern to the hand
        returns None
        """
        try:
            # to widen the fan, change the multiplicative of amplitude
            rotation_amplitude: int | float = (len(card_list) - 1) * 10
            rotation_step: float = rotation_amplitude / (len(card_list) - 1)
        except ZeroDivisionError:
            rotation_amplitude, rotation_step = 0, 0
        # rotation is set to rotation of the first card from the left
        rotation:float = self.angle + rotation_amplitude / 2
        self.radius: int | float = 200
        self.cards.clear()

        for card in card_list.values():
            sin_rotation: float = math.sin(math.radians(rotation))
            cos_rotation: float = math.cos(math.radians(rotation))
            # calculate where along the circle with r = radius the card is located
            center_x: float = self.center[0] - self.radius * sin_rotation
            center_y: float = self.center[1] - self.radius * cos_rotation
            
            # rotate the card by rotation and place at P(center_x, center_y)
            card.rotate_and_move(rotation, (center_x,center_y))
            card.location = card.rect.center
            card.rotation = rotation
            rotation -= rotation_step
            
            # add card to group
            self.add(card)
            self.cards[card.name] = card

    def add_(self, card: PokerCard | None) -> None:

        try:
            if card != PokerCard:
                raise AttributeError
            self.empty()
            self.cards[card.name] = card
            self.add_cards(self.cards.copy())
        except AttributeError:
            pass
        
    def edit_masks(self) -> None: 
        cards = self.sprites()
        for index, card in enumerate(cards):
            for other_card in cards[index+1:]:
                pos_card = card.rect.topleft
                pos_other = other_card.rect.topleft
                offset = (pos_other[0] - pos_card[0], pos_other[1] - pos_card[1])
                card.mask.erase(other_card.mask, offset)
 
    def adjust_position_based_on_mouse_pos(self) -> None:
        for card in self.sprites():
            card.adjust_position_based_on_mouse_pos()
            
    def remove_on_click(self, mouse1_state: bool) -> tuple[str, list[PokerCard]] | tuple[None, None]:
        for card in self.sprites():
            if card.is_clicked(mouse1_state):
                del self.cards[card.name]
                self.empty()
                self.add_cards(self.cards.copy())
                return card.name, card
        return None, None
    
    def remove_card(self, card_name: str) -> PokerCard:
        card: PokerCard = self.cards.pop(card_name)
        self.empty()
        self.add_cards(self.cards.copy())
        return card


    def flip(self):
        for card in self.sprites():
            card.flip()

    def set_unmovable(self):
        for card in self.sprites():
            card.mobile = False
    
    def set_movable(self):
        for card in self.sprites():
            card.mobile = True
        
