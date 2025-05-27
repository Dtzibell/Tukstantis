############################################
# Tukstantis
#
# The goal of the game is to collect 1000 points.
# 
# The goal is achieved by collecting poker cards that each have an assigned value:
# - The A is 11 points
# - 10 is 10 points
# - The K is 4 points
# - The Q is 3 points
# - The J is 2 points
# - The 9 is 0 points
#  
# The cards are collected in rounds. Each round, 3 players are handed 7 cards, and 3
# leftover cards are left in the center of the table. The round begins with a bidding
# war, where each player bids how many points they can gather within the round.
# The bidding war starts at 100 (this may raise questions that will be elaborated on later).
#
# After the bidding phase, the player who bid the most receives the cards in the center
# and sorts out 3 cards that they do not need. Then, they begin by laying their first card.
# 
# The first card being laid per turn is the base card of the turn. The goal of the other players
# is to beat it by laying a more valuable card of the same type. If they do not have a card
# that is more valuable of the same type, they have to give away a card from their hand of the
# same type. If they do not have a card of the same type in their hand, they have to give up any 
# other card.
# 
# This way, the largest amount of points that could be collected would be 120:
# 11*4 + 10*4 + 4*4 + 3*4 + 2*4 = 120. So how come does the bidding war start at 100? The catch is: 
# a pair of a king and a queen of the same type (further - royal couple) also has a value if placed on the board:
# - Spades - 40
# - Clubs - 60
# - Diamonds - 80
# - Hearts - 100
# If one half of the royal couple is placed on the board (and called), the sum of all collected cards + the 
# value of the royal couple (or couples, if you are lucky) determine how many points you
# gathered. If you did not manage to gather the points you bid however, the bid is subtracted 
# from your current score (which can go into the negatives). If other players manage to snatch
# cards away from you, they get the points for their collected cards, and may also call their
# royal couple.
# 
# When a royal couple is called, all the cards of the same type become trump cards which can
# beat any card that is not of the same type (the trump card hierarchy remains the same). So 
# think carefully about calling your royal couples!
# 
# If you like to play risky and more fun - bids can be made without looking at your cards. This
# way, you can earn twice the points that you bid if you manage gather them. You opponents will
# also gain double the points that they gather, and if you do not manage to gather the points
# that you bid, you lose double the points.
# 
# The game finalizes once one player climbs over 1000 points. However, if a player reaches 900
# points, they have three rounds to win a bid. If they fail to do so, 100 points are deducted
# from their result. Additionally, players who reach 900 points do not gain any points from
# rounds during which other players won the bid.
# 
# Now, feel free to try the game out yourself! There might be rules that I have missed, please
# point it out.
# 
# 
# 
# 



# Assets used in this game:
# font 0xprotonerdfontmono
# cards' art from: https://code.google.com/archive/p/vector-playing-cards/
# cards' back art from: https://www.vecteezy.com/vector-art/102977-playing-card-back-free-vector

import pygame
from sys import exit
from pathlib import Path
import random
from game_initiation import initialize_cards, generate_player_hands, generate_player_bets, generate_card_backs
from ButtonText import Button
from auction_manager import manage_auction
from socket_manager.server import run_server
import time

# random.seed(0)

sock, socket_purpose = run_server()
if socket_purpose == "server":
    # seed = random.randint(0, 2**200)
    seed = 1
    for client in sock.clients:
        sock.socket.sendto(seed.to_bytes(25), (client[0], client[1]))
    random.seed(seed)
elif socket_purpose == "connect":
    msg, sender = sock.socket.recvfrom(1024)
    seed = int.from_bytes(msg)
    random.seed(seed)

# initialize cards
path_to_cards = Path("PNG-cards-1.3")
card_height = 200 # used to maintain card scale
card_width = card_height * 0.636 # 0.636 is the ratio between width and height
all_cards: list = initialize_cards(path_to_cards, card_width, card_height)

# initialize display
pygame.init()
screen: pygame.Surface = pygame.display.set_mode((1280,800))
screen.fill("grey")
pygame.display.set_caption("Tūkstantis")
clock = pygame.time.Clock()

# initalize player hands
path_to_card_back = path_to_cards / "back_of_card.png"
player_dict, center_hand = generate_player_hands(all_cards, path_to_card_back, 
                                                sock.player_no, card_width, card_height)

# initialize game state
phase = "auction"
raise_button = Button((1000, 675), (200, 50), "Raise")
pass_button = Button((1000, 750), (200, 50), "Pass")
show_button = Button((640,750), (200, 50), "Show cards")
player_name = f"player{sock.player_no}"
for player in player_dict.values():
    player[0].set_unmovable()
show_show_button = True
player_dict = generate_player_bets(player_dict)
mouse1_state = False
turn = random.randint(0,2)

while True:
    # handle application closing
    if pygame.event.peek(pygame.QUIT):
        pygame.quit()
        exit()
    
    # handle the state of mouse1
    if pygame.event.peek(pygame.MOUSEBUTTONDOWN):
        mouse1_state = True
    else:
        mouse1_state = False
    
    pygame.event.clear()

    screen.fill("grey")
    player_hand = player_dict[player_name][0]


    if phase == "auction":
        # update cards
        
        player_hand.edit_masks()
        player_hand.update_auction()
        for player in player_dict.values():
            player[0].draw(screen)

        if show_show_button:
            show_button.draw(screen, mouse1_state)
            if show_button.pressed:
                show_show_button = False
                show_button.pressed = False
                player_hand.empty()
                player_hand.add_cards(player_hand.cards)
                player_hand.set_movable()

        center_hand.draw(screen)
        # update current bet
        for player in player_dict.values():
            player[2].draw(screen, "black")
        
        if turn == sock.player_no:
            # update game state
            raise_button.draw(screen, mouse1_state)
            pass_button.draw(screen, mouse1_state)
            turn, end_auction = manage_auction(turn, player_name, raise_button,
                                               pass_button, player_dict)
            to_transfer = [player_name, str(player_dict[player_name][2].value), str(turn), str(end_auction)]
            to_transfer:str = ":".join(to_transfer)
            to_transfer = to_transfer.encode()
            for client in sock.clients:
                sock.socket.sendto(to_transfer, client)
        
        else:
            try:
                auction_info, server = sock.socket.recvfrom(1024)
                auction_info = auction_info.decode().split(":")
                player_dict[auction_info[0]][2].value = int(auction_info[1])
                turn = int(auction_info[2])
                end_auction = int(auction_info[3])
            except IndexError:
                print("packet lost")
                pass
    
    # transition into card sort
    if end_auction:
        end_auction = 0
        phase = "card sort"
        
        # find out the index of the winner
        for key, values in player_dict.items(): # player is list [PlayerHand, CollectedHand, Bet]
            # checks if players bet is 0
            if values[2].value != 0: # if Bet is not 0
                winner_name = key # winner is the player whose bet is not 0
                winner_hand = player_dict[winner_name][0]
                winner_cards = winner_hand.cards
                if winner_name == player_name:
                    confirm_button = Button((1000,750), (200,50), "Confirm")
                    center_cards = center_hand.cards
                    center_hand.empty()
                    winner_hand.empty()
                    new_winner_cards = winner_cards + center_cards
                    winner_hand.add_cards(new_winner_cards)
                else:
                    # adds ten card backs to winner's hand
                    new_card_backs = generate_card_backs(path_to_card_back, 10, card_width, card_height)
                    winner_hand.empty()
                    winner_hand.add_cards(new_card_backs)
                    # if show button has not been pressed, reveals the cards
                    if show_show_button:
                        player_hand.empty()
                        player_hand.add_cards(player_hand.cards)
                        player_hand.set_movable()
                break
        
    if phase == "card sort":
        
        # draw hands
        if winner_name == player_name:
            player_hand.edit_masks()
            player_hand.update_card_sort(mouse1_state, player_dict[player_name][1])
            confirm_button.draw(screen, mouse1_state)
            raise_button.draw(screen, mouse1_state)
            player_bet = player_dict[player_name][2]
            player_collected_hand = player_dict[player_name][1]
            if raise_button.pressed:
                player_bet.value += 10
            player_bet.draw(screen, "black")
            if confirm_button.pressed and len(player_collected_hand.sprites()) == 3:
                phase = "fight"
            to_transfer = [phase, str(len(player_collected_hand.sprites()))]
            to_transfer = ":".join(to_transfer)
            for client in sock.clients:
                sock.socket.sendto(to_transfer.encode(), client)
        else:
            card_sort_info, sender = sock.socket.recvfrom(1024)
            card_sort_info = card_sort_info.decode().split(":")
            player_hand.edit_masks()
            # update auction is meant to disallow clicking on the cards
            player_hand.update_auction()
            winner_collected_hand = player_dict[winner_name][1]
            phase = card_sort_info[0]
            new_collected_hand_len = int(card_sort_info[1])
            diff_lens = len(winner_collected_hand.sprites()) - new_collected_hand_len
            if diff_lens != 0:
                collected_backs = generate_card_backs(path_to_card_back, new_collected_hand_len, card_width, card_height)
                player_backs = generate_card_backs(path_to_card_back, 10 - new_collected_hand_len, card_width, card_height)
                winner_collected_hand.empty()
                winner_collected_hand.add_cards(collected_backs)
                winner_hand.empty()
                winner_hand.add_cards(player_backs)

        for player in player_dict.values():
            player[0].draw(screen)
        
        # update card collection
        for player in player_dict.values():
            player[1].update(mouse1_state, player_dict[player_name])
            player[1].draw(screen)
        
    if phase == "fight":
        player_dict[player_name][0].edit_masks()
        player_dict[player_name][0].update_auction()
        player_dict[player_name][1].update(mouse1_state, player_dict)
        for player in player_dict.values():
            player[0].draw(screen)
            player[1].draw(screen)
        player_dict[player_name][2].draw(screen, "black")

    # draw all elements and update screen
    pygame.display.update()
    clock.tick(60)