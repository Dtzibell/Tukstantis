import math
import pygame
from pathlib import Path

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
        self.image = self.image_original.copy()

        # self.rect must be defined to be able to blit it on screen
        center_coords = (card_width / 2, card_height / 2)
        self.rect:pygame.Rect = self.image.get_rect(center = (center_coords))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.mobile = True
        self.rotation = 0 
        self.location = center_coords

        # for printing
        self.name:str = path_to_png.stem
        self.dimens = (card_width, card_height)
        
    def rotate_and_move(self, rotation:float, center_coords: tuple[float,float]) -> None:
        """
        Rotates the image by -rotation and then gets the center of its rectangle at center_coords.
        Returns None
        """
        self.image = pygame.transform.rotate(self.image_original, rotation)
        self.rect = self.image.get_rect(center = center_coords)
        self.mask = pygame.mask.from_surface(self.image)

    def update_auction(self) -> None:
        """
        updates the card during the auction phase
        """
        if self.mobile: # self.mobile is shut off during certain phases and events
            mouse_pos: tuple[float,float] = pygame.mouse.get_pos()
            
            # since masks always are at the top left corner of the screen
            # the mouse pos has to be offset
            mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            center: tuple[float,float] = self.rect.center

            # the cards move out of the hand when they are hovered over. To achieve this
            # approximate locations are computed for normal and hovered states of the card
            approximate_original = pygame.Rect(self.location[0] - 5, self.location[1] - 5,
                                               20, 20)
            approximate_popout = pygame.Rect(self.location[0] - 5 - 100 * math.sin(math.radians(self.rotation)),
                                             self.location[1] - 5 -  100 * math.cos(math.radians(self.rotation)),
                                             20, 20)
            
            # if self.rect is not hovered, it returns an IndexError
            try:
                
                # if card is hovered and not yet at popout position
                if (self.mask.get_at(mouse_pos) and 
                    not approximate_popout.collidepoint(self.rect.center)):
                    
                    #card is moved up every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] - 10 * math.sin(math.radians(self.rotation)),
                                          center[1] - 10 * math.cos(math.radians(self.rotation))))

                # if card.rect is hovered but not card.mask and card not at original position 
                elif (not self.mask.get_at(mouse_pos) and 
                      not approximate_original.collidepoint(self.rect.center)):
                    
                    # card is moved down every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 10 * math.sin(math.radians(self.rotation)),
                                          center[1] + 10 * math.cos(math.radians(self.rotation))))
            
            except IndexError:
                # if card is not yet at origin
                if not approximate_original.collidepoint(self.rect.center):
                    
                    # card is moved down every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 10 * math.sin(math.radians(self.rotation)),
                                          center[1] + 10 * math.cos(math.radians(self.rotation))))
    
    def update_card_sort(self, mouse1_state: bool) -> bool:
        """
        updates the card state in card sort phase
        returns killed - whether the card in the hand was pressed during this phase
        """
        killed = False
        
        # refer to update auction TODO: make a seperate function?
        if self.mobile:
            mouse_pos: tuple[float,float] = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            center: tuple[float,float] = self.rect.center
            approximate_original = pygame.Rect(self.location[0] - 10, self.location[1] - 10,
                                               20, 20)
            approximate_popout = pygame.Rect(self.location[0] - 10 - 100 * math.sin(math.radians(self.rotation)),
                                             self.location[1] - 10 -  100 * math.cos(math.radians(self.rotation)),
                                             20, 20)
            try:
                if (self.mask.get_at(mouse_pos) and 
                    not approximate_popout.collidepoint(self.rect.center)):
                    
                    self.rotate_and_move(self.rotation, 
                                         (center[0] - 10 * math.sin(math.radians(self.rotation)),
                                          center[1] - 10 * math.cos(math.radians(self.rotation))))
                    
                elif (not self.mask.get_at(mouse_pos) and 
                      not approximate_original.collidepoint(self.rect.center)):
                    
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 10 * math.sin(math.radians(self.rotation)),
                                          center[1] + 10 * math.cos(math.radians(self.rotation))))
                    
            except IndexError:
                if not approximate_original.collidepoint(self.rect.center):
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 10 * math.sin(math.radians(self.rotation)),
                                          center[1] + 10 * math.cos(math.radians(self.rotation))))
            
            # allows interaction with the cards if player0 is the winner
            try:
                if self.mask.get_at(mouse_pos) and mouse1_state:
                    # removes card from all groups and changes killed
                    self.kill()
                    killed = True
            except IndexError:
                pass
            
        return killed
    
    def update_collected(self, mouse1_state: bool, player_list: dict):
        """
        updates cards in CollectedCards
        """

        try:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            
            # if a card in CollectedCards is pressed
            if self.mask.get_at(mouse_pos) and mouse1_state:
                self.kill()
                
                # gets list of current cards in hand
                cards = player_list[0].sprites()
                cards.append(self)
                #removes all cards and adds new cards
                player_list[0].empty()
                player_list[0].add_cards(cards)
            else:
                pass
        except IndexError:
            pass

    def __str__(self):
        return f"PokerCard({self.name})"
    
    def __repr__(self):
        return f"PokerCard({self.name})"