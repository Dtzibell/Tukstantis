import math
from pathlib import Path
import sys
import pygame

IntFloatTuple = tuple[int | float, int | float]

class PokerCard(pygame.sprite.Sprite):
    def __init__(self, card_width: float | int, card_height: float | int, path_to_png: Path,
                 path_to_card_back: Path) -> None:
        """
        A PokerCard is a subclass of pygame.sprite.Sprite.
        It has the following attributes:
        image_front - a pygame.Surface that represents the front of the card.
        image_back - a pygame.Surface that represents the back of the card.
        image - a pygame.Surface that represents the the side of the card that 
        is currently being shown.
        side - string of the side of the object currently being drawn.
        location - tuple(x,y) center coordinates of the object.
        rotation - int | float rotation of the object.
        rect - the objects pygame.Rect.
        mask - the objects pygame.Mask.
        mobile - bool that determines whether the object is movable.
        name - string of the stem of the png file (name of card).
        dimens - tuple(width, height) of the card.
        value - int of the value of the card (according to the rules).
        card_type - string of the type of the card (clubs, hearts etc.).
        """
        super().__init__()
        
        self.image_front: pygame.Surface = pygame.image.load(path_to_png)
        self.image_front = pygame.transform.scale(self.image_front, (card_width, card_height))
        # copy is needed to retain image quailty. Transform methods ruin it.
        self.image_back: pygame.Surface = pygame.image.load(path_to_card_back)
        self.image_back = pygame.transform.scale(self.image_back, (card_width, card_height))
        self.current_image = self.image_back
        self.image: pygame.Surface = self.current_image.copy()

        # self.rect must be defined to be able to blit.
        self.location: IntFloatTuple = (card_width / 2, card_height / 2)
        self.rotation: int | float = 0 
        self.rect: pygame.Rect = self.image.get_rect(center = (self.location))
        self.mask: pygame.Mask = pygame.mask.from_surface(self.image)
        
        self.mobile: bool = False

        self.name: str = path_to_png.stem
        self.dimens: IntFloatTuple = (card_width, card_height)
        
        value_index = self.name.index("_")
        try:
            self.value = int(self.name[:value_index])
        except ValueError:
            pass
        
        type_index = self.name.rindex("_")
        self.card_type: str = self.name[type_index:]

    def rotate_and_move(self, rotation: int | float, center_coords: IntFloatTuple) -> None:
        """
        Rotates the image by -rotation and then gets the center of its rectangle at center_coords.
        Returns None
        """
        self.image = pygame.transform.rotate(self.current_image, rotation)
        self.rotation = rotation
        self.rect = self.image.get_rect(center = center_coords)
        self.mask = pygame.mask.from_surface(self.image)

    def flip(self) -> None:
        """
        Flip the card on the other side.
        """
        if self.current_image == self.image_back:
            self.current_image = self.image_front
        else: self.current_image = self.image_back
        self.rotate_and_move(self.rotation, self.location)

    def get_mouse_pos_relative_to_mask(self) -> IntFloatTuple:
        """
        Gets mask-relative mouse position.
        """
        mouse_pos: IntFloatTuple = pygame.mouse.get_pos()
        # mouse pos has to be offset because card masks are only at the top
        # left of the screen
        mouse_pos: IntFloatTuple = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        return mouse_pos

    def get_approximate_movements(self, outward_movement: int | float) -> tuple[pygame.Rect, pygame.Rect]:
        """
        the cards move out of the hand when they are hovered over. To achieve this
        approximate locations are computed for normal and hovered states of the card
        """

        sin_rotation: float = math.sin(math.radians(self.rotation))
        cos_rotation: float = math.cos(math.radians(self.rotation))
        approximate_original_location = pygame.Rect(self.location[0] - 10, 
                                                    self.location[1] - 10,
                                                    20, 20)
        approximate_float = pygame.Rect(self.location[0] - 10 - outward_movement * sin_rotation,
                                        self.location[1] - 10 - outward_movement * cos_rotation,
                                        20, 20)
        return approximate_original_location, approximate_float

    def adjust_position_based_on_mouse_pos(self) -> None:
        """
        Function that determines card's position when hovered.
        """
        if self.mobile: # self.mobile is shut off during certain phases and events
            relative_mouse_pos: IntFloatTuple = self.get_mouse_pos_relative_to_mask()
            center: IntFloatTuple= self.rect.center
            sin_rotation: float = math.sin(math.radians(self.rotation))
            cos_rotation: float = math.cos(math.radians(self.rotation))

            approximate_original_location, approximate_float_position =\
                    self.get_approximate_movements(100)
            # if self.rect is not hovered, it returns an IndexError
            try:

                # if card is hovered and not yet at float position
                if (self.mask.get_at(relative_mouse_pos) and 
                    not approximate_float_position.collidepoint(self.rect.center)):
                    
                    #card is moved up every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] - 8 * sin_rotation,
                                          center[1] - 8 * cos_rotation))

                # if card.rect is hovered but not card.mask and card not at original position 
                elif (not self.mask.get_at(relative_mouse_pos) and 
                      not approximate_original_location.collidepoint(self.rect.center)):
                    
                    # card is moved down every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 8 * sin_rotation,
                                          center[1] + 8 * cos_rotation))
            
            except IndexError:
                # if card is not yet at origin
                if not approximate_original_location.collidepoint(self.rect.center):
                    
                    # card is moved down every frame
                    self.rotate_and_move(self.rotation, 
                                         (center[0] + 8 * sin_rotation,
                                          center[1] + 8 * cos_rotation))
    
    def is_clicked(self, mouse1_state):
        try:
            mouse_pos = self.get_mouse_pos_relative_to_mask()
            if self.mask.get_at(mouse_pos) and mouse1_state and self.mobile:
                self.kill()
                return True
            else: return False
        except IndexError:
            return False

    def __str__(self):
        return f"PokerCard({self.name})"
    
    def __repr__(self):
        return f"PokerCard({self.name})"


if __name__ == "__main__":
    pygame.init()
    path_to_card_pngs = Path("/home/dtzi/Desktop/Tukstantis/card_pngs")
    screen = pygame.display.set_mode((1280,800))
    clock = pygame.time.Clock()
    card = PokerCard(0.636*200, 200, path_to_card_pngs / "10_of_clubs.png", path_to_card_pngs / "back_of_card.png")
    card.rotate_and_move(30, (640,400))
    group = pygame.sprite.GroupSingle(card)
    while True:
        if pygame.event.peek(pygame.QUIT):
            pygame.quit()
            sys.exit()
        mouse1_state = pygame.event.peek(pygame.MOUSEBUTTONDOWN)
        pygame.event.clear()
        screen.fill("grey")
        if mouse1_state and card.mask.get_at(card.get_mouse_pos_relative_to_mask()):
            card.flip()
        card.update()
        group.draw(screen)
        pygame.display.update()
        clock.tick(60)
