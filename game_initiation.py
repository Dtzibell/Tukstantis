from CardClasses.PokerCard import PokerCard
import random
from pathlib import Path
from CardClasses.PlayerHand import PlayerHand
from CardClasses.CollectedHand import CollectedHand
from CardClasses.AuctionCards import AuctionCards
from ButtonText import Bet
from CardClasses.PlayerClass import Player

def initialize_cards(path_to_pngs: Path, card_width: float, card_height: float) -> dict[str, PokerCard]:
    """
    creates card objects from every png in the png folder (except card back)
    """
    
    card_back: Path = path_to_pngs / "back_of_card.png"
    card_deck: dict[str, PokerCard] = dict()
    for card_front in path_to_pngs.glob("*.png"):
        card_name: str = card_front.stem
        if card_name == "back_of_card":
            continue
        current_card = PokerCard(card_width, card_height, card_front, card_back)
        card_deck[card_name] = current_card
    return card_deck

def generate_player_cards(all_cards:dict[str, PokerCard]) -> tuple[dict[str, PokerCard], dict[str, PokerCard]]:
    """
    Creates a hand of 7 cards from a list of cards
    """

    card_names: list[str] = random.sample(list(all_cards), 7)
    hand = dict()
    for card in card_names:
        hand[card] = all_cards[card]
        del all_cards[card]
        
    return hand, all_cards

def generate_initial_state(all_cards: dict[str, PokerCard], player_no: int):
    """
    Generates all necessary card groups.
    Each of the items reaching the final Player object have to be shiffled
    by the players number. This way, the active player always shows up at the bottom
    of the screen.
    """
    
    cards_player0, leftover_cards = generate_player_cards(all_cards)
    cards_player1, leftover_cards = generate_player_cards(leftover_cards)
    cards_player2, leftover_cards = generate_player_cards(leftover_cards)
    auction_cards = AuctionCards()
    auction_cards.add_(leftover_cards)

    player_cards = [cards_player0, cards_player1, cards_player2]
    # this ensures that the hand object at the bottom of the screen receives
    # the player_index cards.
    player_cards = player_cards[player_no:] + player_cards[:player_no]
    hand0 = PlayerHand((640, 900), 0)
    hand1 = PlayerHand((-100, 400), -90)
    hand2 = PlayerHand((1380, 400), 90)
    player_hands: list[PlayerHand] = [hand0, hand1, hand2]
    for i in range(len(player_hands)):
        player_hands[i].add_cards(player_cards[i])
    # this ensures that the players cards are drawn at the bottom of the screen
    player_hands = player_hands[player_no:] + player_hands[:player_no]

    collected_player0 = CollectedHand((325, 625), 0)
    collected_player1 = CollectedHand((150, 100), -90)
    collected_player2 = CollectedHand((1080, 100), 90)
    collected_cards = [collected_player0, collected_player1, collected_player2]
    # cards drawn at the bottom of the screen
    collected_cards = collected_cards[player_no:] + collected_cards[:player_no]
    
    bet1 = Bet((640, 470), 0)
    bet2 = Bet((250, 400), -90)
    bet3 = Bet((1030, 400), 90)
    player_bets = [bet1, bet2, bet3]
    # drawn at the bottom of the screen
    player_bets = player_bets[player_no:] + player_bets[:player_no]

    player_center = Player(player_hands[0], collected_cards[0], player_bets[0])
    player_left = Player(player_hands[1], collected_cards[1], player_bets[1])
    player_right = Player(player_hands[2], collected_cards[2], player_bets[2])
    players = [player_center, player_left, player_right]
    # this ensures that the code can access the player object by the player index
    players = players[player_no:] + players[:player_no]
    return players, auction_cards

def regenerate_initial_state(all_cards: dict[str, PokerCard], players: list[Player]):
    """
    This func can definitely be further optimized. Do I need all the extra objects?
    """

    cards_player0, leftover_cards = generate_player_cards(all_cards)
    cards_player1, leftover_cards = generate_player_cards(leftover_cards)
    cards_player2, leftover_cards = generate_player_cards(leftover_cards)
    auction_hand = AuctionCards()
    auction_hand.add_(leftover_cards)
    player_cards = [cards_player0, cards_player1, cards_player2]
    
    for i, player in enumerate(players):
        player.hand.add_cards(player_cards[i])
        for card_name in player.collected.cards.copy().keys():
            player.collected.remove_card(card_name)
        player.bet.set_value(100)

    return players, auction_hand
