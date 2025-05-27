from ButtonText import Button
from ButtonText import Bet

def is_finished(player_dict: dict):
    """
    returns whether the auction has ended.
    """
    
    passed = 0
    end_auction = 0

    for player in player_dict.values():
        if player[2].value == 0:
            passed += 1
    if passed == 2:
        end_auction = 1

    return end_auction

    
def manage_auction(turn: int, player_name: str, raise_button: Button, pass_button: Button, player_dict: dict):
    """
    manages the auction
    """
    # get how many passed, end auction if two
    end_auction = is_finished(player_dict)
    if end_auction:
        return turn, end_auction
        
    # if own turn
    if turn == int(player_name[-1]) and player_dict[player_name][2].value != 0:
        # if raising
        if raise_button.pressed:
            bets_values = [player_dict[player][2].value for player in player_dict.keys()]
            player_dict[player_name][2].value = max(bets_values) + 10
            print(player_dict[player_name][2].value)
            turn += 1 # INTEGERS ARE IMMUTABLE!
            raise_button.pressed = False
        
        #if passing
        elif pass_button.pressed:
            player_dict[player_name][2].value = 0
            turn += 1
            pass_button.pressed = False

    # if already passed, skips the turn
    elif player_dict[player_name][2].value == 0:
        turn += 1
    
    if turn == 3:
        turn = 0
    
    return turn, end_auction