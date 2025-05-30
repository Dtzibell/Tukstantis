from ButtonText import Button
from ButtonText import Bet
from CardClasses.PlayerClass import Player

def is_finished(players: list[Player]):
    """
    returns whether the auction has ended.
    """
    
    passed = 0
    end_auction = 0

    for player in players:
        if player.bet.value == 0:
            passed += 1
    if passed == 2:
        end_auction = 1

    return end_auction

    
def manage_auction(turn: int, player_index: int, raise_button: Button, pass_button: Button, players: list[Player]):
    """
    manages the auction
    """
    # get how many passed, end auction if two
    end_auction = is_finished(players)
    if end_auction:
        return turn, end_auction

    players[player_index].bet = players[player_index].bet
        
    # if own turn
    if turn == player_index and players[player_index].bet.value != 0:
        # if raising
        if raise_button.pressed:
            bets_values = [players[player_index].bet.value for player_index in range(3)]
            players[player_index].bet.value = max(bets_values) + 10
            print(players[player_index].bet.value)
            turn += 1 # INTEGERS ARE IMMUTABLE!
            raise_button.pressed = False
        
        #if passing
        elif pass_button.pressed:
            players[player_index].bet.value = 0
            turn += 1
            pass_button.pressed = False

    # if already passed, skips the turn
    elif players[player_index].bet.value == 0:
        turn += 1
    
    if turn == 3:
        turn = 0
    
    return turn, end_auction
