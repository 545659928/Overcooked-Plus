import pygame


class Color:
    BLACK = (0, 0, 0)
    FLOOR = (245, 230, 210)  # light gray
    COUNTER = (220, 170, 110)   # tan/gray
    COUNTER_BORDER = (114, 93, 51)  # darker tan
    DELIVERY = (96, 96, 96)  # grey
    BLOCK = (139, 69, 19) #dark brown
    BLOCK_BORDER = (0, 0, 0) #black
    PROGRESS_BAR = (0, 255, 0)  # green
    PROGRESS_BAR_BG = (255, 0, 0)  # red

KeyToTuple = {
    pygame.K_UP    : ( 0, -1),  #273
    pygame.K_DOWN  : ( 0,  1),  #274
    pygame.K_RIGHT : ( 1,  0),  #275
    pygame.K_LEFT  : (-1,  0),  #276
}
