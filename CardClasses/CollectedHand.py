from CardClasses.PokerCard import PokerCard
import pygame

class CollectedHand(pygame.sprite.LayeredUpdates):
    def __init__(self, center_coords: tuple[float,float], rotation: int):
        super().__init__()
        self.center = center_coords
        self.rotation = rotation
        self.top_layer = 0
        self.cards = dict()
    
    def add_(self, card: PokerCard | None):
        
        try:
            card.rotate_and_move(self.rotation, self.center)
            self.add(card)
            self.cards[card.name] = card
            self.change_layer(card, self.top_layer)
        except AttributeError:
            pass

    def remove_on_click(self, mouse1_state) -> tuple[str, PokerCard] | tuple[None, None]:
        try:
            card = self.get_top_sprite()
            if card.is_clicked(mouse1_state):
                del self.cards[card.name]
                self.remove(card)
                return card.name, card
            return None, None
        except IndexError:
            return None, None

    def remove_card(self, card_name: str) -> PokerCard:
        card = self.cards.pop(card_name)
        card.remove(card)
        return card
