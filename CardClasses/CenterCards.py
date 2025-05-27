from CardClasses.PokerCard import PokerCard
import pygame
from pathlib import Path

class CenterCards(pygame.sprite.LayeredUpdates):
    def __init__(self, cards: list[PokerCard]) -> None:
        super().__init__()
        self.cards = cards
    
    def add_cards(self, card_list: list[PokerCard], card_gap: int):
        
        card_width = card_list[0].dimens[0]
        card_height = card_list[0].dimens[1]
        center = (640, 400)
        offset = -card_width - card_gap
        for n in range(len(card_list)):
            card_back = PokerCard(card_width, card_height, Path("PNG-cards-1.3/back_of_card.png"))
            card_back.rotate_and_move(0, (center[0] + offset, center[1]))
            self.add(card_back)
            offset += card_width + card_gap