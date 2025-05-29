import pygame
from sys import exit
from pathlib import Path
import random
from game_initiation import initialize_cards, generate_card_backs, generate_players
from ButtonText import Button
from auction_manager import manage_auction
from socket_manager.server import run_server

sock, socket_purpose = run_server()
if socket_purpose == "host":
    # seed = random.randint(0, 2**200)
    seed = 1
    for client in sock.clients:
        sock.socket.sendto(seed.to_bytes(25), (client[0], client[1]))
    random.seed(seed)
elif socket_purpose == "client":
    msg, sender = sock.socket.recvfrom(1024)
    seed = int.from_bytes(msg)
    random.seed(seed)
player_index = sock.player_no

# initialize cards
path_to_card_pngs = Path("card_pngs")
card_height = 200 # used to maintain card scale
card_width = card_height * 0.636 # 0.636 is the ratio between width and height
all_cards: list = initialize_cards(path_to_card_pngs, card_width, card_height)

# initialize display
pygame.init()
screen: pygame.Surface = pygame.display.set_mode((1280,800))
screen.fill("grey")
pygame.display.set_caption("Tūkstantis")
clock = pygame.time.Clock()

# initalize player hands
path_to_card_back = path_to_card_pngs / "back_of_card.png"
players, center_cards = generate_players(all_cards, path_to_card_back, 
                                player_index, card_width, card_height)
player_hand = players[player_index].hand
player_collected_cards = players[player_index].collected
player_bet = players[player_index].bet

# initialize game state
phase = "auction"
raise_button = Button((1000, 675), (200, 50), "Raise")
pass_button = Button((1000, 750), (200, 50), "Pass")
show_button = Button((640,750), (200, 50), "Show cards")
show_show_button = True
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

    if phase == "auction":
        # update cards
        
        player_hand.edit_masks()
        player_hand.adjust_position_based_on_mouse_pos()
        for player in players:
            player.hand.draw(screen)

        if show_show_button:
            show_button.draw(screen, mouse1_state)
            if show_button.pressed:
                show_show_button = False
                show_button.pressed = False
                player_hand.empty()
                player_hand.add_cards(player_hand.cards)
                player_hand.set_movable()

        center_cards.draw(screen)
        # update current bet
        for player in players: 
            player.bet.draw(screen, "black")
        
        if turn == player_index:
            # update game state
            raise_button.draw(screen, mouse1_state)
            pass_button.draw(screen, mouse1_state)
            turn, end_auction = manage_auction(turn, player_index, raise_button,
                                               pass_button, players)
            to_transfer = [str(player_index), str(player_bet.value), str(turn), str(end_auction)]
            to_transfer = sock.convert_list_to_bytes(to_transfer)
            for client in sock.clients:
                sock.socket.sendto(to_transfer, client)
        
        else:
            try:
                auction_info, server = sock.socket.recvfrom(1024)
                auction_info = sock.convert_bytes_to_list(auction_info)
                players[auction_info[0]].bet.value = auction_info[1]
                turn = auction_info[2]
                end_auction = auction_info[3]
            except IndexError:
                print("packet lost")
                pass
    
    # transition into card sort
    if end_auction:
        end_auction = 0
        phase = "card sort"
        
        # find out the index of the winner
        for player in players: # player is list [PlayerHand, CollectedHand, Bet]
            # checks if players bet is 0
            if player.bet.value != 0: # if Bet is not 0
                winner = player # winner is the player whose bet is not 0
                winner_hand = winner.hand
                winner_cards = winner_hand.cards
                winner_collected = winner.collected
                winner_bet = winner.bet
                if winner == players[player_index]:
                    confirm_button = Button((1000,750), (200,50), "Confirm")
                    center_cards_ = center_cards.cards
                    center_cards.empty()
                    winner_hand.empty()
                    new_winner_cards = winner_cards + center_cards_
                    winner_hand.add_cards(new_winner_cards)
                    winner_hand.set_movable()
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
        if winner == players[player_index]:
            player_hand.edit_masks()
            player_hand.adjust_position_based_on_mouse_pos()
            moved = player_hand.move_to_collected_cards_on_click(mouse1_state, winner)
            confirm_button.draw(screen, mouse1_state)
            raise_button.draw(screen, mouse1_state)
            if raise_button.pressed:
                player_bet.value += 10
            player_bet.draw(screen, "black")
            if confirm_button.pressed and len(player_collected_cards.sprites()) == 3:
                phase = "fight"
            to_transfer = [phase, str(len(player_collected_cards.sprites()))]
            to_transfer = sock.convert_list_to_bytes(to_transfer)
            for client in sock.clients:
                sock.socket.sendto(to_transfer, client)
        else:
            card_sort_info, sender = sock.socket.recvfrom(1024)
            card_sort_info = sock.convert_bytes_to_list(card_sort_info)
            player_hand.edit_masks()
            # update auction is meant to disallow clicking on the cards
            player_hand.adjust_position_based_on_mouse_pos()
            phase = card_sort_info[0]
            new_collected_hand_len = int(card_sort_info[1])
            diff_lens = len(winner_collected.sprites()) - new_collected_hand_len
            if diff_lens != 0:
                collected_backs = generate_card_backs(path_to_card_back, new_collected_hand_len, card_width, card_height)
                player_backs = generate_card_backs(path_to_card_back, 10 - new_collected_hand_len, card_width, card_height)
                winner_collected.empty()
                winner_collected.add_cards(collected_backs)
                winner_hand.empty()
                winner_hand.add_cards(player_backs)

        for player in players:
            player.hand.draw(screen)
        
        # update card collection
        for player in players:
            player.collected.update(mouse1_state, player)
            player.collected.draw(screen)
        
    if phase == "fight":
        players[player_index].hand.edit_masks()
        players[player_index].hand.adjust_position_based_on_mouse_pos()
        for player in players:
            player.hand.draw(screen)
            player.collected.draw(screen)
        winner.bet.draw(screen, "black")

    # draw all elements and update screen
    pygame.display.update()
    clock.tick(60)
