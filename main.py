import pygame
from sys import exit
from pathlib import Path
import random
from CardClasses.CollectedHand import CollectedHand
from CardClasses.PlayerHand import PlayerHand
from CardClasses.PlayerClass import Player
from CardClasses.PokerCard import PokerCard
from CardClasses.AuctionCards import AuctionCards
from game_initiation import initialize_cards, generate_initial_state
from ButtonText import Bet, Button
from auction_manager import manage_auction
from socket_manager.server import run_server
import json
from typing import Any

sock, socket_purpose = run_server()
if socket_purpose == "host":
    # seed = random.randint(0, 2**200)
    seed = 1
    for client in sock.clients:
        sock.socket.sendto(seed.to_bytes(25), (client[0], client[1]))
    random.seed(seed)
elif socket_purpose == "client":
    msg, sender = sock.socket.recvfrom(1024)
    seed: int = int.from_bytes(msg)
    random.seed(seed)
player_index: int = sock.player_no

# initialize cards
path_to_card_pngs: Path = Path("card_pngs")
card_height: int | float = 200 # used to maintain card scale
card_width: int | float = card_height * 0.636 # 0.636 is the ratio between width and height
all_cards: dict[str, PokerCard] = initialize_cards(path_to_card_pngs, card_width, card_height)

# initialize display
pygame.init()
screen: pygame.Surface = pygame.display.set_mode((1280,800))
screen.fill("grey")
pygame.display.set_caption("Tūkstantis")
clock: pygame.time.Clock = pygame.time.Clock()

# initalize player hands
path_to_card_back: Path = path_to_card_pngs / "back_of_card.png"
players, auction_hand = generate_initial_state(all_cards, player_index)
player_obj: Player = players[player_index]
player_hand: PlayerHand = player_obj.hand
player_collected_cards: CollectedHand = player_obj.collected
player_bet: Bet = player_obj.bet

# initialize game state
phase: str = "auction"
raise_button: Button= Button((1000, 675), (200, 50), "Raise")
pass_button: Button = Button((1000, 750), (200, 50), "Pass")
show_button: Button = Button((640,750), (200, 50), "Show cards")
show_show_button: bool = True
turn: int = random.randint(0,2)
end_auction: bool = False

while True:
    # handle application closing
    if pygame.event.peek(pygame.QUIT):
        pygame.quit()
        exit()
    
    # handle the state of mouse1
    mouse1_state: bool = pygame.event.peek(pygame.MOUSEBUTTONDOWN)
    
    pygame.event.clear()
    screen.fill("grey")

    if phase == "auction":
        # draw all cards
        player_hand.edit_masks()
        player_hand.adjust_position_based_on_mouse_pos()
        for player in players:
            player.hand.draw(screen)
        auction_hand.draw(screen)

        # draw show button
        if show_show_button:
            show_button.draw(screen, mouse1_state)
            if show_button.pressed:
                show_show_button: bool = False
                show_button.pressed = False
                player_hand.flip()
                player_hand.set_movable()

        # draw bets
        for player in players: 
            player.bet.draw(screen, "black")
        
        # own turn
        if turn == player_index:
            # update game state
            raise_button.draw(screen, mouse1_state)
            pass_button.draw(screen, mouse1_state)
            turn, end_auction = manage_auction(turn, player_index, raise_button,
                                               pass_button, players)
            to_transfer: list[Any] = [player_index, player_bet.value, turn, end_auction]
            json_dump: bytes = json.dumps(to_transfer).encode()
            for client in sock.clients:
                sock.socket.sendto(json_dump, client)
        # other's turn
        else:
            try:
                auction_info_bytes, server = sock.socket.recvfrom(1024)
                auction_info = json.loads(auction_info_bytes)
                players[auction_info[0]].bet.set_value(auction_info[1])
                turn = auction_info[2]
                end_auction = auction_info[3]
            except IndexError:
                print("packet lost")
                pass

    
    # transition phase
    if end_auction:
        # unset end_auction to stop looping this conditional
        end_auction = False
        phase = "card sort"
        
        # find out the index of the winner
        winner: Player = players[turn]
        winner_index: int = turn
        winner_hand: PlayerHand = winner.hand
        # winner_cards is a list of all cards in the hand
        winner_cards: dict[str,PokerCard] = winner_hand.cards
        winner_collected: CollectedHand = winner.collected
        winner_bet: Bet = winner.bet

        # if self winner
        if winner == player_obj:
            confirm_button: Button = Button((1000,750), (200,50), "Confirm")
            auction_cards: dict[str, PokerCard] = auction_hand.cards
            # places center_cards into self hand
            auction_hand.empty()
            winner_hand.empty()
            winner_cards.update(auction_cards)
            winner_hand.add_cards(winner_cards.copy())
            if show_show_button:
                winner_hand.flip()
            else:
                for card in winner_hand.sprites():
                    if card.current_image == card.image_back:
                        card.flip()
            winner_hand.set_movable()
                
        # if other winner
        else:
            # adds ten card backs to winner's hand
            # replaces the 7 card backs with 10 cards backs
            auction_cards = auction_hand.cards
            auction_hand.empty()
            winner_hand.empty()
            winner_cards.update(auction_cards)
            winner_hand.add_cards(winner_cards.copy())
            # if show button has not been pressed, reveals the cards
            if show_show_button:
                player_hand.flip()
                player_hand.set_movable()
        
    if phase == "card sort":
        
        player_hand.edit_masks()
        player_hand.adjust_position_based_on_mouse_pos()
        for player in players:
            player.hand.draw(screen)
            player.collected.draw(screen)
            winner.bet.draw(screen, "black")

        if winner == player_obj:
            confirm_button.draw(screen, mouse1_state)
            if confirm_button.pressed and len(player_hand) == 7:
                phase = "round"
                round_leader = winner_index
            elif confirm_button.pressed:
                print("You have to have 7 cards")
            card_hand_name, card_hand = winner_hand.remove_on_click(mouse1_state)
            card_collected_name, card_collected = winner_collected.remove_on_click(mouse1_state)
            winner_collected.add_(card_hand)
            winner_hand.add_(card_collected)
            to_transfer = [phase, card_hand_name, card_collected_name]
            json_dump = json.dumps(to_transfer).encode()
            for client in sock.clients:
                sock.socket.sendto(json_dump, client)
        
        else:
            card_sort_info_bytes, sender = sock.socket.recvfrom(1024)
            card_sort_info = json.loads(card_sort_info_bytes)
            phase = card_sort_info[0]
            card_hand_name = card_sort_info[1]
            card_collected_name = card_sort_info[2]
            if card_hand_name == None:
                pass
            else:
                card = winner_hand.remove_card(card_hand_name)
                winner_collected.add_(card)
            if card_collected_name == None:
                pass
            else:
                card = winner_collected.remove_card(card_collected_name)
                winner_hand.add_(card)
            if phase == "round":
                round_leader = winner

    if phase == "round":
        players[player_index].hand.edit_masks()
        players[player_index].hand.adjust_position_based_on_mouse_pos()
        for player in players:
            player.hand.draw(screen)
            player.collected.draw(screen)
        winner.bet.draw(screen, "black")
        if turn == round_leader:
            players[round_leader].hand.move_to_board_on_click(mouse1_state, board_center)

        

    # draw all elements and update screen
    pygame.display.update()
    clock.tick(60)
