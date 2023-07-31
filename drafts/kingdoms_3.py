# Qin Kingdoms 2023

""" TODOs:
- attach unit info to each maphex; allow movement
- make larger map in memory (board dict), allow scrolling
- add armies; allow movement
- for large maps, use random seed terrain types and grow the pieces around them,
instead of creating from top-left downward.

AI combat moves
- move towards enemy, if you are stronger
- move towards rice, if rice unguarded
- move away from enemies, if more castles than can be occupied
- set fire, if outnumbered
- harder: split to defend archers from enemy
AI reward LOG: min losses, max enemy losses, +500 winning +100 for each captured general
"""
import time
import random
import sys
import pygame
from pygame import Color
DEBUG = False
BACKGROUND = (20, 20, 20)
HEIGHT = 600
WIDTH = 800
BLUE = (30, 175, 80)
BOARD_EDGE = [20, 20, WIDTH-20, HEIGHT-20] # top, left, right, bottom
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surf = pygame.display.get_surface()
board_segs = pygame.sprite.Group()
pygame.key.set_repeat(100, 100)
font = pygame.font.Font('freesansbold.ttf', 28)

images = {
    'p': pygame.image.load("tile-plains.png").convert(),
    'm': pygame.image.load("tile-mtn.png").convert(),
    'h': pygame.image.load("tile-hills.png").convert(),
    's': pygame.image.load("tile-swamp.png").convert(),
    'w': pygame.image.load("tile-water.png").convert(),
    'c': pygame.image.load("tile-castle.png").convert(),
}
extra_images = {
    'a': pygame.image.load("tile-army.png").convert(),
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

def offset(xx, tile=66):
    if xx % 2 == 0:
        y_offset = int(0.5 * tile)
    else:
        y_offset = 0
    return y_offset

def make_board():
    tile = 66
    last_piece_type = None
    last_piece_positions = {'p':0, 'm':1, 'h':2, 's':3, 'w':4, 'c':5}
    board = {}    
    for xx in range(10):
        for yy in range(7):
            y_offset = offset(xx)
            x = (xx * tile)
            y = int((yy * tile) + y_offset)

            # picking terrain type
            tiles = list(images.keys())
            weights = [20, 15, 15, 10, 0, 0]
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


class ActiveCursor:
    def __init__(self, x, y):
        self.tile = 66
        self.edge = 33
        self.rect = pygame.Rect(self.edge + x*self.tile, self.edge + y*self.tile + offset(x), self.tile, self.tile)
        self.cursor = self.rect
    def draw(self, screen):
        # last param (3) is the width, for transparent rect
        if time.time() % 1 > 0.5:
            pygame.draw.rect(screen, Color("black"), self.cursor, 3)
        else:
            pygame.draw.rect(screen, Color("white"), self.cursor, 3)
    def update(self, active_spot):
        (x,y) = active_spot
        self.rect = pygame.Rect(self.edge + x*self.tile, self.edge + y*self.tile + offset(x), self.tile, self.tile)
        self.cursor = self.rect


class Army(pygame.sprite.Sprite):
    """ must include type and general in kwargs"""
    types = {
        0:'militia',
        1:'infantry', 2:'heavy infantry', 3:'pikemen',
        4:'archers', 5:'calvary', 6:'balistas',        
        7:'horsebowmen', 8:'crossbowmen',
        9:'alchemists', 10:'skyriders', 11:'ninjas',
        12:'medics', 13:'firebombers', 14:'storms'
    }
    def __init__(self, board, xx, yy, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.xx = xx
        self.yy = yy
        for k,v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'type'):
            self.type = 1
        if not hasattr(self, 'moves'):
            self.moves = 6
        self.image = extra_images['a']
        self.image_key = 'a'
        self.size = 12300        
        edge = 33
        tile = 66
        self.rect = pygame.Rect(self.xx*tile, edge + self.yy*tile + offset(self.xx) + 3, self.image.get_width(), self.image.get_height())
        shorthand = str(int(self.size / 100))
        self.text = font.render(shorthand, True, Color("white"), Color("black"))
    def draw(self):
        surf.blit(self.image, self.rect.midtop)
        surf.blit(self.text, self.rect.midtop)

    def update(self, board_state, keys):
        """Checks:
        - keys match allowed moves
        - new spot is not occupied
        TODO - has enough movement points for terrrain
        - new spot is not off board
        """
        x, y = board_state.active_spot
        prv = False
        nxt = False
        if keys[pygame.K_7]:
            x -= 1
            if x % 2 == 0:
                y -= 1
        elif keys[pygame.K_UP] or keys[pygame.K_8]:
            y -= 1
        elif keys[pygame.K_9]:
            x += 1
            if x % 2 == 0:
                y -= 1
        elif keys[pygame.K_1]:
            x -= 1
            if x % 2 != 0:
                y += 1
        elif keys[pygame.K_DOWN] or keys[pygame.K_2]:
            y += 1
        elif keys[pygame.K_3]:
            x += 1
            if x % 2 != 0:
                y += 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_4]:
            prv = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_6]:
                nxt = True
        if (board_state.on_board((x,y)) and board_state.has_army((x,y)) is False and
            (x != board_state.active_spot[0] or y != board_state.active_spot[1])
            ):
            self.xx = x
            self.yy = y
            edge = 33
            tile = 66
            self.rect = pygame.Rect(self.xx*tile, edge + self.yy*tile + offset(self.xx) + 3, self.image.get_width(), self.image.get_height())
            self.draw()
            # update board_state now
            # put terrain back
            board_state.board[(board_state.active_spot[0], board_state.active_spot[1])].draw()
            # remove army from prev board spot
            delattr(board_state.board[(board_state.active_spot[0], board_state.active_spot[1])], 'army')
            # copy self into new board spot
            board_state.board[(x,y)].army = self
            #board_state.active_spot = (x,y) ### handled in game loop with next_army()
            return board_state, True
        else:
            print(f"DEBUG {x,y}")
            print(f"DEBUG x {x != board_state.active_spot[0]} y {y != board_state.active_spot[1]}")
            print(f"DEBUG army {board_state.has_army((x,y))} and on_board {board_state.on_board((x,y))}")
            print(f"{sum(keys)} {(board_state.active_spot[0], board_state.active_spot[1])}")
            return board_state, False


class BoardState():
    def __init__(self, armies=None, **kwargs):
        self.board = make_board()
        self.board = add_river(self.board)
        self.armies = []
        if not armies:
            self.army_spots = [(1,6), (4,4), (6,6)] # starting spots
        for _new in self.army_spots:
            self.board[_new].army = Army(self.board, _new[0], _new[1], type=1, moves=6)
            self.armies.append(self.board[_new].army)
        #self.armies = [v.army for spot,v in self.board.items() if hasattr(v,'army')]
        self.a = 0 # active army index        
        self.active_army = self.armies[self.a]
        self.active_spot = self.army_spots[self.a]
        for k,v in kwargs.items():
            setattr(self, k, v)
    def has_army(self, spot):
        for xy, piece in self.board.items():
            if spot == xy and hasattr(piece, 'army'):
                return True
        return False
    def on_board(self, spot):
        return True if spot in self.board.keys() else False
    def next_army(self):        
        self.a += 1
        if self.a > (len(self.armies)-1):
            print('next turn')
            self.a = 0
        self.active_army = self.armies[self.a]
        self.active_spot = (self.armies[self.a].xx, self.armies[self.a].yy)


def game_loop():
    clock = pygame.time.Clock()
    screen.fill(BACKGROUND)
    bs = BoardState() # makes board; adds default armies    
    cursor = ActiveCursor(*bs.active_spot)
    [a.draw() for a in bs.armies]

    while True:
        cursor.draw(screen)
        pygame.display.flip()
        clock.tick(60)        
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and sum(keys) > 0:                
                bs, successful = bs.active_army.update(bs, keys) # Army doesn't contain board_state; its within it
                if successful is True:
                    bs.next_army()
                    cursor.update(bs.active_spot)
                # BUG: next army copies this move if this army had an unsuccessful move.

        
if __name__ == "__main__":
    game_loop()