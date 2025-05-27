from CardClasses.PokerCard import PokerCard
import random
from pathlib import Path
from CardClasses.PlayerHand import PlayerHand
from CardClasses.CollectedCards import CollectedCards
from CardClasses.CenterCards import CenterCards
from ButtonText import Bet
from collections import defaultdict

def initialize_cards(path_to_pngs: Path, width: float, height: float) -> list:
    """
    Adds all possible card objects into a list
    returns a list of them
    """
    
    all_cards = []
    for card in path_to_pngs.glob("*.png"):
        card_name: str = card.stem
        if card_name == "back_of_card":
            continue
        current_card = PokerCard(width, height, card)
        all_cards.append(current_card)
    return all_cards

def generate_hand(all_cards:list[PokerCard]) -> tuple[list, list]:
    """
    Creates a hand of 7 cards from a list of cards
    """

    hand = random.sample(all_cards, 7)
    for card in hand:
        all_cards.remove(card)
    return hand, all_cards

def generate_player_hands(all_cards: list[PokerCard], path_to_card_back: Path, 
                          player_no: int, card_width: float, card_height: float):
    """
    Generates all necessary card groups.
    """
    
    cards_player0, leftover_cards = generate_hand(all_cards)
    cards_player1, leftover_cards = generate_hand(leftover_cards)
    cards_player2, center_cards = generate_hand(leftover_cards)
    player_cards = [cards_player0, cards_player1, cards_player2]
    player_cards = player_cards[player_no:] + player_cards[:player_no]

    card_backs_player0 = generate_card_backs(path_to_card_back, 7, card_width, card_height)
    card_backs_player1 = generate_card_backs(path_to_card_back, 7, card_width, card_height)
    card_backs_player2 = generate_card_backs(path_to_card_back, 7, card_width, card_height)
    card_backs = [card_backs_player0, card_backs_player1, card_backs_player2]

    hand1 = PlayerHand((640, 900), 0, 200, player_cards[0])
    hand2 = PlayerHand((-100, 400), -90, 200, player_cards[1])
    hand3 = PlayerHand((1380, 400), 90, 200, player_cards[2])
    player_hands = [hand1, hand2, hand3]
    for i in range(len(player_hands)):
        player_hands[i].add_cards(card_backs[i])
    # player_hands = player_hands[player_no:] + player_hands[:player_no]
    
    center_hand = CenterCards(center_cards)
    center_hand.add_cards(center_cards, 50)
    
    collected_player0 = CollectedCards((350, 650), 0)
    collected_player1 = CollectedCards((150, 100), -90)
    collected_player2 = CollectedCards((1080, 100), 90)
    collected_hands = [collected_player0, collected_player1, collected_player2] 
    # collected_hands = collected_hands[player_no:] + collected_hands[:player_no]

    keys = ["player0", "player1", "player2"]
    keys = keys[player_no:] + keys[:player_no]
    card_dictionary = defaultdict(list)
    for i,key in enumerate(keys):
        card_dictionary[key].extend([player_hands[i], collected_hands[i]])

    return card_dictionary, center_hand


def generate_card_backs(path_to_back: Path, no: int, card_width: float, card_height: float):
    """
    generates groups of 7 card backs for PlayerHands
    """
    card_backs = []
    for n in range(no):
        card_backs.append(PokerCard(card_width,card_height,path_to_back))
    return card_backs

def generate_player_bets(card_dict: dict):
    """
    initializes player bets for the auction
    """

    # card_dict is "player0" : player_hands1, collected_cards1 etc.
    bet1 = Bet((640, 550), 0)
    bet2 = Bet((250, 400), -90)
    bet3 = Bet((1030, 400), 90)
    player_bets = [bet1, bet2, bet3]
    for i, key in enumerate(card_dict.keys()):
        card_dict[key].append(player_bets[i])
    return card_dict