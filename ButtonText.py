import pygame
import math

class Button():
    def __init__(self, center_coords: tuple[int, int], size: tuple[int, int], text: str) -> None:
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

        self.center: tuple[int, int] = center_coords
        self.size: tuple[int, int] = size
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
        text: Text = Text(self.center, self.text, 0, 30)
        text.draw(screen, "white")

class Text():
    def __init__(self, center_coords: tuple[int, int], text: str, rotation: int, size: int) -> None:
        self.center: tuple[int, int] = center_coords
        self.text: str = text
        self.rotation: int = rotation
        self.size: int = size
    
    def draw(self, screen: pygame.Surface, color: str) -> None:
        text_font: pygame.font.Font = pygame.font.SysFont("Arial", self.size)
        if "\n" in self.text:
            sin = math.sin(math.radians(self.rotation))
            cos = math.cos(math.radians(self.rotation))
            lines = self.text.split("\n")
            line_height = text_font.get_height() * cos
            line_width = text_font.get_height() * sin
            total_height = line_height * len(lines)
            total_width = line_height * len(lines)
            start_height = self.center[1] - total_height // 2 + line_height // 2
            start_width = self.center[0] - total_width // 2 + line_width // 2
            for i, line in enumerate(lines):
                rendered_line = text_font.render(line, True, color)
                rendered_line = pygame.transform.rotate(rendered_line, self.rotation)
                text_rect = rendered_line.get_rect(center=(start_width + i * line_width, start_height + i * line_height))
                screen.blit(rendered_line, text_rect)
        else:
            text: pygame.Surface = text_font.render(self.text, True, color)
            text = pygame.transform.rotate(text, self.rotation)
            text_rect: pygame.Rect = text.get_rect(center = self.center)
            screen.blit(text, text_rect)
    
class Bet(Text):
    def __init__(self, center_coords: tuple[int, int], rotation: int) -> None:
        self.center = center_coords
        self.rotation = rotation
        self.value = 100
        self.text = str(self.value)
        self.size = 30

    def set_value(self, value: int) -> None:

        self.value = value
        self.text = str(value)
