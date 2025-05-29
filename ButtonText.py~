import pygame
class Button():
    def __init__(self, center_coords: tuple[int,int], size: tuple[int,int], text: str) -> None:
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

        self.center = center_coords
        self.size = size
        self.text = text
        self.surface = pygame.surface.Surface(self.size)
        self.rect = self.surface.get_rect(center = self.center)
        self.pressed = False
    
    def draw(self, screen: pygame.Surface, mouse1_state: bool):
        """
        draws the button on the screen
        """
        # if hovered over
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # if mouse1 is pressed, fills with red, otherwise grey
            if mouse1_state:
                self.pressed = True
                self.surface.fill((255,0,0))
            else:
                self.pressed = False
                self.surface.fill((75,75,75))
        #if not hovered over
        else:
            self.surface.fill("black")
        screen.blit(self.surface, self.rect)
        
        #creates and draws text over the Buttons Surface
        text = Text(self.center, self.text, 0)
        text.draw(screen, "white")

        # text_font = pygame.font.SysFont("0xprotonerdfontmono", 30)
        # text = text_font.render(self.text, True, "white")
        # text_rect = text.get_rect(center = self.center)
        # screen.blit(text, text_rect)

class Text():
    def __init__(self, center_coords: tuple[int,int], text: str, rotation: int):
        self.center = center_coords
        self.text = text
        self.rotation = rotation
    
    def draw(self, screen: pygame.Surface, color: str):
        text_font = pygame.font.SysFont("0xprotonerdfontmono", 30)
        text = text_font.render(self.text, True, color)
        text = pygame.transform.rotate(text, self.rotation)
        text_rect = text.get_rect(center = self.center)
        screen.blit(text, text_rect)

class Bet(Text):
    def __init__(self, center_coords: tuple[int,int], rotation: int):
        self.center = center_coords
        self.rotation = rotation
        self.value = 100
        self.text = str(self.value)

    def draw(self, screen: pygame.Surface, color: str):
        text_font = pygame.font.SysFont("0xprotonerdfontmono", 30)
        text = text_font.render(str(self.value), True, color)
        text = pygame.transform.rotate(text, self.rotation)
        text_rect = text.get_rect(center = self.center)
        screen.blit(text, text_rect)