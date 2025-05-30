from CardClasses.PokerCard import PokerCard
import random
from pathlib import Path
from CardClasses.PlayerHand import PlayerHand
from CardClasses.CollectedCards import CollectedCards
from CardClasses.CenterCards import CenterCards
from ButtonText import Bet
from collections import defaultdict
from CardClasses.PlayerClass import Player

def initialize_cards(path_to_pngs: Path, card_width: float, card_height: float) -> list:
    """
    creates card objects from every png in the png folder (except card back)
    """
    
    card_deck = []
    for card in path_to_pngs.glob("*.png"):
        card_name: str = card.stem
        if card_name == "back_of_card":
            continue
        current_card = PokerCard(card_width, card_height, card)
        card_deck.append(current_card)
    return card_deck

def generate_player_cards(all_cards:list[PokerCard]) -> tuple[list, list]:
    """
    Creates a hand of 7 cards from a list of cards
    """

    hand = random.sample(all_cards, 7)
    for card in hand:
        all_cards.remove(card)
    return hand, all_cards

def generate_card_backs(path_to_card_back: Path, amount: int, card_width: float, card_height: float):
    """
    generates groups of 7 card backs for PlayerHands
    """
    card_backs = []
    for n in range(amount):
        card_backs.append(PokerCard(card_width,card_height,path_to_card_back))
    return card_backs

def generate_players(all_cards: list[PokerCard], path_to_card_back: Path, 
                          player_no: int, card_width: float, card_height: float):
    """
    Generates all necessary card groups.
    Each of the items reaching the final Player object have to be shuffled
    by the players number. This way, the active player always shows up at the bottom
    of the screen.
    """
    
    cards_player0, leftover_cards = generate_player_cards(all_cards)
    cards_player1, leftover_cards = generate_player_cards(leftover_cards)
    cards_player2, leftover_cards = generate_player_cards(leftover_cards)
    center_cards = CenterCards(leftover_cards)
    center_cards.add_cards(leftover_cards, 50, path_to_card_back)

    player_cards = [cards_player0, cards_player1, cards_player2]
    player_cards = player_cards[player_no:] + player_cards[:player_no]
    hand0 = PlayerHand((640, 900), 0, 200, player_cards[0])
    hand1 = PlayerHand((-100, 400), -90, 200, player_cards[1])
    hand2 = PlayerHand((1380, 400), 90, 200, player_cards[2])
    player_hands = [hand0, hand1, hand2]
    player_hands = player_hands[player_no:] + player_hands[:player_no]

    card_backs_player0 = generate_card_backs(path_to_card_back, 7, card_width, card_height)
    card_backs_player1 = generate_card_backs(path_to_card_back, 7, card_width, card_height)
    card_backs_player2 = generate_card_backs(path_to_card_back, 7, card_width, card_height)
    card_backs = [card_backs_player0, card_backs_player1, card_backs_player2]
    # card backs arent shuffled by player_no because theyre all identical anyway

    for i in range(len(player_hands)):
        # card backs are displayed, but player_cards are retained in the object
        # game needs to be initiated without showing cards.
        player_hands[i].add_cards(card_backs[i])
    
    collected_player0 = CollectedCards((350, 650), 0)
    collected_player1 = CollectedCards((150, 100), -90)
    collected_player2 = CollectedCards((1080, 100), 90)
    collected_cards = [collected_player0, collected_player1, collected_player2] 
    collected_cards = collected_cards[player_no:] + collected_cards[:player_no]
    
    bet1 = Bet((640, 550), 0)
    bet2 = Bet((250, 400), -90)
    bet3 = Bet((1030, 400), 90)
    player_bets = [bet1, bet2, bet3]
    player_bets = player_bets[player_no:] + player_bets[:player_no]

    player_center = Player(player_hands[0], collected_cards[0], player_bets[0])
    player_left = Player(player_hands[1], collected_cards[1], player_bets[1])
    player_right = Player(player_hands[2], collected_cards[2], player_bets[2])
    players = [player_center, player_left, player_right]
    players = players[player_no:] + players[:player_no]
    return players, center_cards
