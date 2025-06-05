from CardClasses.PokerCard import PokerCard
import pygame

class AuctionCards(pygame.sprite.LayeredUpdates):
    def __init__(self) -> None:
        """
        AuctionCards is always three cards
        """

        super().__init__()
        self.center: tuple[int,int] = (640, 400)
        self.gap: int = 50
        self.cards: dict[str, PokerCard] = dict()

    def add_(self, cards: dict[str, PokerCard]) -> None:
        
        card_width: int | float = 200
        for card in cards.values():
            # offset is negative when length is less than 2
            offset = (card_width + self.gap) * (len(self.cards) - 1)
            card.rotate_and_move(0, (self.center[0] + offset, self.center[1]))
            self.cards[card.name] = card
            self.add(card)
