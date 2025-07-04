from ButtonText import Button
from ButtonText import Bet
from CardClasses.PlayerClass import Player
import unittest

def is_finished(players: list[Player]):
    """
    returns whether the auction has ended.
    """
    
    passed = 0
    end_auction = False

    for player in players:
        if player.bet.value == 0:
            passed += 1

    if passed == 2:
        end_auction = True

    return end_auction

    
def manage_auction(turn: int, player_index: int, raise_button: Button, pass_button: Button, players: list[Player]):
    """
    manages the auction
    """
    if players[player_index].bet.value == 0:
        turn = (turn + 1) % 3
        end_auction = False
        return turn, end_auction

    # get how many passed, end auction if two
    end_auction = is_finished(players)
    if end_auction:
        return turn, end_auction
    
    # if own turn
    if turn == player_index:
        # if raising
        if raise_button.pressed:
            bets_values = [players[player_index].bet.value for player_index in range(3)]
            players[player_index].bet.set_value(max(bets_values) + 10) 
            turn = (turn + 1) % 3
        
        #if passing
        elif pass_button.pressed:
            players[player_index].bet.set_value(0)
            turn = (turn + 1) % 3

    # if already passed, skips the turn
    return turn, end_auction
