import pygame
from CardClasses.PokerCard import PokerCard

class BoardCards(pygame.sprite.LayeredUpdates):

    def __init__(self):
        super().__init__()
        self.center: tuple[int, int] = (640, 250)
        self.cards: dict[str, PokerCard] = dict()
        self.offset = 50
        
    def add_(self, card: PokerCard | None, turn: int) -> int:
        try: 
            if type(card) != PokerCard:
                raise AttributeError
            if card.current_image == card.image_back:
                card.flip()
            card.rotate_and_move(0, (self.center[0], self.center[1] + self.offset * (len(self.cards) - 1)))
            card.rotation = 0
            card.location = (self.center[0], self.center[1] + self.offset * (len(self.cards) - 1))
            self.add(card)
            self.cards[card.name] = card
            self.change_layer(card, len(self.cards))
            turn = (turn + 1) % 3
            return turn
        except AttributeError:
            return turn 

    def remove_all(self) -> list[PokerCard]:
        removed: list[PokerCard] = list()
        for card in self.cards.values():
            self.remove(card)
            removed.append(card)
        self.cards.clear()
        return removed
            

