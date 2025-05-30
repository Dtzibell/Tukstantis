import math
import pygame
from pathlib import Path
from CardClasses.PlayerClass import Player

class PokerCard(pygame.sprite.Sprite):
    def __init__(self, card_width: float, card_height: float, path_to_png: Path) -> None:
        """
        A PokerCard is a subclass of pygame.sprite.Sprite.
        It has the following attributes:
        image - a pygame.Surface that represents the png of the PokerCard
        rect - a pygame.Rect that represents the rectangle of the object
        mask - pygame.mask.Mask of the object
        name - string of the stem of the png file (name of card)
        dimens - tuple(width, height) of the card
        
        These are only initialized after the group of the cards is drawn 
                                    (retrieved from the group's function):
        location - tuple(width,height) of the location of the object on the first draw
        rotation - int of the rotation of the object on the first draw
        returns None
        """
        super().__init__()
        
        self.image_original:pygame.Surface = pygame.image.load(path_to_png)
        self.image_original = pygame.transform.scale(self.image_original, (card_width, card_height))
        # copy is needed to retain image quailty. Transform methods ruin it.
        self.image = self.image_original.copy()

        # self.rect must be defined to be able to blit.
        self.location = (card_width / 2, card_height / 2)
        self.rotation = 0 
        self.rect:pygame.Rect = self.image.get_rect(center = (self.location))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.mobile = False

        self.name:str = path_to_png.stem
        self.dimens = (card_width, card_height)
        
        value_index = self.name.index("_")
        try:
            self.value = int(self.name[:value_index])
        except ValueError:
            pass
        
        type_index = self.name.rindex("_")
        self.card_type = self.name[type_index:]

    def rotate_and_move(self, rotation:float, center_coords: tuple[float,float]) -> None:
        """
        Rotates the image by -rotation and then gets the center of its rectangle at center_coords.
        Returns None
        """
        self.image = pygame.transform.rotate(self.image_original, rotation)
        self.rect = self.image.get_rect(center = center_coords)
        self.mask = pygame.mask.from_surface(self.image)
    def get_mouse_pos_relative_to_mask(self):
        mouse_pos = pygame.mouse.get_pos()
        # mouse pos has to be offset because card masks are only at the top
        # left of the screen
        mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        return mouse_pos

    def get_approximate_movements(self, outward_movement):
        # the cards move out of the hand when they are hovered over. To achieve this
        # approximate locations are computed for normal and hovered states of the card
        sin_rotation = math.sin(math.radians(self.rotation))
        cos_rotation = math.cos(math.radians(self.rotation))
        approximate_original_location = pygame.Rect(self.location[0] - 5, 
                                                    self.location[1] - 5,
                                                    20, 20)
        approximate_float = pygame.Rect(self.location[0] - 5 - outward_movement * sin_rotation,
                                        self.location[1] - 5 - outward_movement * cos_rotation,
                                        20, 20)
        return approximate_original_location, approximate_float

    def adjust_position_based_on_mouse_pos(self) -> None:
        """
        updates the card during the auction phase
        """
        if self.mobile: # self.mobile is shut off during certain phases and events
            relative_mouse_pos = self.get_mouse_pos_relative_to_mask()
            center = self.rect.center
            sin_rotation = math.sin(math.radians(self.rotation))
            cos_rotation = math.cos(math.radians(self.rotation))

            approximate_original_location, approximate_float_position =\
                    self.get_approximate_movements(100)
            # if self.rect is not hovered, it returns an IndexError
            try:

                # if card is hovered and not yet at float position
                if (self.mask.get_at(relative_mouse_pos) and 
                    not approximate_float_position.collidepoint(self.rect.center)):
                    
                    #card is moved up every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] - 10 * sin_rotation,
                                          center[1] - 10 * cos_rotation))

                # if card.rect is hovered but not card.mask and card not at original position 
                elif (not self.mask.get_at(relative_mouse_pos) and 
                      not approximate_original_location.collidepoint(self.rect.center)):
                    
                    # card is moved down every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 10 * sin_rotation,
                                          center[1] + 10 * cos_rotation))
            
            except IndexError:
                # if card is not yet at origin
                if not approximate_original_location.collidepoint(self.rect.center):
                    
                    # card is moved down every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 10 * sin_rotation,
                                          center[1] + 10 * cos_rotation))
    
    def move_to_collected_cards(self,mouse1_state):
        
        moved = False
        try:
            mouse_pos = self.get_mouse_pos_relative_to_mask()   
            # if a card in CollectedCards is pressed
            if self.mask.get_at(mouse_pos) and mouse1_state:
                self.kill()
                moved = True
        except IndexError:
            pass
        return moved


    def move_to_hand(self, mouse1_state: bool, player):
        """
        updates cards in CollectedCards
        """
        try:
            mouse_pos = self.get_mouse_pos_relative_to_mask()            
            # if a card in CollectedCards is pressed
            if self.mask.get_at(mouse_pos) and mouse1_state:
                self.kill()
                
                # gets list of current cards in hand
                cards = player.hand.sprites()
                cards.append(self)
                #removes all cards and adds new cards
                player.hand.empty()
                player.hand.add_cards(cards)
        except IndexError:
            pass

    def __str__(self):
        return f"PokerCard({self.name})"
    
    def __repr__(self):
        return f"PokerCard({self.name})"
