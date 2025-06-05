import pygame
from CardClasses.PokerCard import IntFloatTuple

class Button():
    def __init__(self, center_coords: IntFloatTuple, size: IntFloatTuple, text: str) -> None:
        """
        Button class for handling user inputs
        Has the following attributes:
        center - tuple(width,height) of Button location (based on object's center)
        size - tuple(width,height) of Button size
        text - string of Button text
        surface - pygame.Surface of Button
        rect - pygame.Rect of Button
        pressed - bool of Button pressed state
        """

        self.center: IntFloatTuple = center_coords
        self.size: IntFloatTuple = size
        self.text: str = text
        self.surface: pygame.Surface = pygame.surface.Surface(self.size)
        self.rect: pygame.Rect = self.surface.get_rect(center = self.center)
        self.pressed: bool = False
    
    def draw(self, screen: pygame.Surface, mouse1_state: bool) -> None:
        """
        draws the button on the screen
        """
        # if hovered over
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # if mouse1 is pressed, fills with red, otherwise grey
            if mouse1_state:
                self.pressed: bool = True
                self.surface.fill((255,0,0))
            else:
                self.pressed: bool = False
                self.surface.fill((75,75,75))
                self.pressed = False
        #if not hovered over
        else:
            self.surface.fill("black")
            self.pressed = False
        screen.blit(self.surface, self.rect)
        
        #creates and draws text over the Buttons Surface
        text: Text = Text(self.center, self.text, 0)
        text.draw(screen, "white")

        # text_font = pygame.font.SysFont("0xprotonerdfontmono", 30)
        # text = text_font.render(self.text, True, "white")
        # text_rect = text.get_rect(center = self.center)
        # screen.blit(text, text_rect)

class Text():
    def __init__(self, center_coords: IntFloatTuple, text: str, rotation: int) -> None:
        self.center: IntFloatTuple = center_coords
        self.text: str = text
        self.rotation: int = rotation
    
    def draw(self, screen: pygame.Surface, color: str):
        text_font = pygame.font.SysFont("0xprotonerdfontmono", 30)
        text = text_font.render(self.text, True, color)
        text = pygame.transform.rotate(text, self.rotation)
        text_rect = text.get_rect(center = self.center)
        screen.blit(text, text_rect)

class Bet(Text):
    def __init__(self, center_coords: IntFloatTuple, rotation: int):
        self.center = center_coords
        self.rotation = rotation
        self.value = 100
        self.text = str(self.value)

    def set_value(self, value: int):

        self.value = value
        self.text = str(value)
