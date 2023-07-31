# Qin Kingdoms 2023, day 1
import random
import sys
import pygame
from pygame import Color

DEBUG = False
HEIGHT = 600
WIDTH = 800
BACKGROUND = (20, 20, 20)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surf = pygame.display.get_surface()
board_segs = pygame.sprite.Group()
pygame.key.set_repeat(100, 100)

images = {
    'p': pygame.image.load("tile-plains.png").convert_alpha(),
    'm': pygame.image.load("tile-mtn.png").convert(),
    'h': pygame.image.load("tile-hills.png").convert(),
    's': pygame.image.load("tile-swamp.png").convert(),
    'w': pygame.image.load("tile-water.png").convert(),
}


class MapHex(pygame.sprite.Sprite):

    def __init__(self, image_key, x, y, xx, yy):
        pygame.sprite.Sprite.__init__(self)
        # rect: coords for each part of board (left, top, width, height)
        self.x = x
        self.y = y
        self.xx = xx
        self.yy = yy
        self.image = images[image_key]
        self.image_key = image_key
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

    def draw(self):
        # WIDTH, HEIGHT, BOX_WIDTH, BOX_HEIGHT        
        surf.blit(self.image, self.rect.center)
        pygame.display.flip()



def make_board():
    tile = 66
    last_piece_type = None
    last_piece_positions = {'p':0, 'm':1, 'h':2, 's':3, 'w':4}
    board = {}    
    for xx in range(10):
        for yy in range(7):
            y_offset = offset(xx)
            x = (xx * tile)
            y = int((yy * tile) + y_offset)

            # picking terrain type
            tiles = list(images.keys())
            weights = [20, 15, 15, 10, 0]
            if last_piece_type:                
                weights[last_piece_positions[last_piece_type]] = 30
            adjacent_tiles = [(xx, yy+1), (xx, yy-1), (xx-1, yy-1), (xx-1, yy+1)]
            for adj in adjacent_tiles:
                if board.get(adj):
                    temp = last_piece_positions[board[adj].image_key]
                    weights[temp] += 5
            #print(weights)                
            image_key = random.choices(tiles, weights, k=1)[0]
            last_piece_type = image_key
            
            piece = MapHex(image_key, x, y, xx, yy)
            piece.draw()
            board[(xx, yy)] = piece
    return board

def offset(xx, tile=66):
    if xx % 2 == 0:
        y_offset = 0.5 * tile
    else:
        y_offset = 0
    return y_offset

def add_river(board):
    """ randomly lays a river through map, starting at top/left edge """
    image_key = 'w'
    tile = 66
    x_range = [min([x for x,y in board.keys()]), max([x for x,y in board.keys()])]
    y_range = [min([y for x,y in board.keys()]), max([y for x,y in board.keys()])]
    top_or_left = random.choice(['top','left'])
    if top_or_left == 'top':
        start = (random.randrange(x_range[0], x_range[1]), 0)
    if top_or_left == 'left':
        start = (0, random.randrange(y_range[0], y_range[1]))
    for i in range(16):
        y_offset = offset(start[0])
        x = (start[0] * tile)
        y = int((start[1] * tile) + y_offset)
        board[start] = MapHex(image_key, x, y, start[0], start[1])
        board[start].draw()
        incr = random.choice([(1,0), (0,1)])
        if board.get( (start[0] + incr[0], start[1] + incr[1]) ):
            start = (start[0] + incr[0], start[1] + incr[1])
        else:
            pass
            #print(f"outside range: {(start[0] + incr[0], start[1] + incr[1])}")
    return board


def game_loop():
    clock = pygame.time.Clock()
    screen.fill(BACKGROUND)
    board = make_board()
    board = add_river(board)

    while True:
        pygame.display.flip()
        clock.tick(60)        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        
if __name__ == "__main__":
    game_loop()
