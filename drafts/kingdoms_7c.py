# Qin Kingdoms 2023

""" TODOs:
[x] 1. random map generator
[x] 2. attach unit info to board (not maphex); allow movement
[x] 3. add multiple armies; allow movement
[x] 4. add generals to armies; count movement points; next army only after finished moving;
[x] 5. mobilize works; player shields; added forests; add enemy armies; basic attacking/defending
[x] 6. subtract troops from attacks;
[x] 7. add castles (a random number, centralized, and adjacent to each other)
[-] 7. increased board size; added game.on_screen to track;
- allow screen to scroll when unit moves close to edge
- prevent starting squares from being in water
- place enemy on castles to start

- capture units when no troops left; store in Player/Enemy for post-combat-
- show error messages on screen, not just print()
- make larger map in memory (board dict), allow scrolling
- add ranged attacks
? for large maps, use random seed terrain types and grow the pieces around them,
instead of creating from top-left downward.
- future: option to redeploy captured generals with 100 men on board (taken from army that defeated it)
    - add warning if loyalty is below 40

AI combat moves
- default: defends castle; barricades
- move towards enemy, if you are stronger
- move towards rice, if rice unguarded
- move away from enemies, if more castles than can be occupied
- set fire, if outnumbered
- harder: split to defend archers from enemy
AI reward LOG: min losses, max enemy losses, +500 winning +100 for each captured general
"""
import math
import time
import random
import sys
import pygame
from pygame import Color
from game_classes import (
    ComputerAI, SpriteSheet,
    random_shield,
    ActiveCursor, General
)

DEBUG = False
BACKGROUND = (20, 20, 20)
HEIGHT = 600
WIDTH = 800
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surf = pygame.display.get_surface()
font = pygame.font.Font('freesansbold.ttf', 28)

images = {
    'p': pygame.image.load("tile-plains.png").convert(),
    'm': pygame.image.load("tile-mtn.png").convert(),
    'h': pygame.image.load("tile-hills.png").convert(),
    's': pygame.image.load("tile-swamp.png").convert(),
    'w': pygame.image.load("tile-water.png").convert(),
    'c': pygame.image.load("tile-castle.png").convert(),
    'f': pygame.image.load("tile-forest.png").convert(),
}
extra_images = {
    'a': pygame.image.load("tile-army.png").convert(),
}

class MapHex(pygame.sprite.Sprite):
    def __init__(self, image_key, pixelx, pixely, x, y):
        pygame.sprite.Sprite.__init__(self)
        # rect: map coords for each part of board (left, top, width, height)
        self.pixelx = pixelx #must adjust when screen shifts
        self.pixely = pixely
        self.x = x # original x (0-15)
        self.y = y # original y (0-11)
        self.image = images[image_key]
        self.image_key = image_key
        self.rect = pygame.Rect(pixelx, pixely, self.image.get_width(), self.image.get_height())
    def draw(self):
        # WIDTH, HEIGHT, BOX_WIDTH, BOX_HEIGHT
        self.rect = pygame.Rect(self.pixelx, self.pixely, self.image.get_width(), self.image.get_height())
        surf.blit(self.image, self.rect.topleft)
        pygame.display.flip()

def make_board(width=16, height=12):
    tile = 66
    last_piece_type = None
    last_piece_positions = {'p':0, 'm':1, 'h':2, 's':3, 'w':4, 'c':5, 'f':6}
    weights = [30, 12, 12, 10, 0, 0, 15]
    board = {}    
    for xx in range(width):
        for yy in range(height):
            y_offset = BoardState.offset(xx)
            x = (xx * tile)
            y = int((yy * tile) + y_offset)

            # picking terrain type
            tiles = list(images.keys())            
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
            # piece.draw()
            board[(xx, yy)] = piece
    return board, width, height

def add_river_and_castles(board):
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
        y_offset = BoardState.offset(start[0])
        x = (start[0] * tile)
        y = int((start[1] * tile) + y_offset)
        board[start] = MapHex(image_key, x, y, start[0], start[1])
        #board[start].draw()
        incr = random.choice([(1,0), (0,1)])
        if board.get( (start[0] + incr[0], start[1] + incr[1]) ):
            start = (start[0] + incr[0], start[1] + incr[1])
        else:
            pass
            #print(f"outside range: {(start[0] + incr[0], start[1] + incr[1])}")
    # add castles
    num_castles = random.choice([1,2,3,3,4,4,5,6])
    img_castle = 'c'
    (xx, yy) = (int(x_range[1]/2), int(y_range[1]/2))
    used_spots = []
    for n in range(num_castles):
        y_offset = BoardState.offset(xx)
        x = (xx * tile)
        y = int((yy * tile) + y_offset)
        board[(xx, yy)] = MapHex(img_castle, x, y, xx, yy)
        #board[(xx, yy)].draw()
        used_spots.append((xx, yy))
        while True:
            adjx = random.choice([1,0,-1])
            adjy = random.choice([1,0,-1])
            if (xx + adjx, yy + adjy) not in used_spots and (adjx != adjy):
                xx += adjx
                yy += adjy
                break            
    return board

def create_armies():
    armies = [] # list of Army objects with Generals
    army_spots = [(2,2)] #, (4,4), (6,6)] # starting spots
    enemy_spots = [] #[(8,3)] #, (6,4)]
    player_shield = random_shield()
    enemy_shield = random_shield()
    if player_shield == enemy_shield:
        enemy_shield = random_shield()
    for spot in army_spots:
        army = Army(spot[0], spot[1],
                    type=1, owner=0,
                    size=random.choice([1333, 2666, 3100, 10100]),
                    shield=player_shield)
        armies.append( army )
    for spot in enemy_spots:
        army = Army(spot[0], spot[1],
                    type=1, owner=1,
                    size=random.choice([4900, 2300, 1250, 10100]),
                    shield=enemy_shield)
        armies.append( army )
    return armies

class Army(pygame.sprite.Sprite, General):
    """ must include type and general in kwargs"""
    types = {
        0:'militia',
        1:'infantry', 2:'heavy infantry', 3:'pikemen',
        4:'archers', 5:'calvary', 6:'balistas',        
        7:'horsebowmen', 8:'crossbowmen',
        9:'alchemists', 10:'skyriders', 11:'ninjas',
        12:'medics', 13:'firebombers', 14:'storms'
    }
    attacks = {
        0:1, 1:3, 2:5, 3:1,
        4:2, 5:5, 6:1, 7:2, 8:2, 9:1, 11:5, 12:1,
    }
    defenses = {
        0:1, 1:3, 2:5, 3:3,
        4:3, 5:2, 6:1, 7:2, 8:3, 9:1, 11:5, 12:1,
    }
    range_attacks = {
        4:2, 6:4, 7:2, 8:4
    }
    unit_moves = {
        0:6, 1:6, 2:6, 3:6, 4:6, 5:10, 6:4, 7:8, 8:6,
        9:6, 10:6, 11:8, 12:6, 13:6, 14:10,
    }
    def __init__(self, x, y, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        for key,val in kwargs.items():
            setattr(self, key, val)
        if not hasattr(self, 'gen'):
            self.gen = General() # creates new general; adds war, int, cha, etc to army.gen
        self.x = x
        self.y = y
        for k,v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'type'):
            self.type = 1
        if not hasattr(self, 'moves'):
            self.moves = self.unit_moves[self.type]
        if not hasattr(self, 'owner'):
            self.owner = 0 # human; 1+ = enemy
        if not hasattr(self, 'size'):
            self.size = 1000
        if not hasattr(self, 'shield'):
            self.shield = random_shield()
        self.attack = self.attacks[self.type]
        self.defense = self.defenses[self.type]
        self.range_attack = self.range_attacks.get(self.type,0)
        self.moves_left = self.moves
        self.mobilize_points = 0
        self.barricade_points = 0
        self.image = extra_images['a']
        self.image_key = 'a'
        self.edge = 33
        self.tile = 66
        self.rect = pygame.Rect(self.x*self.tile, self.edge + self.y*self.tile + BoardState.offset(self.x) + 3, self.image.get_width(), self.image.get_height())
    def shorthand(self):
        return str(int(self.size / 100))
    def spot(self):
        """ must be dynamic, not attribute, & recalculated each time to remain in sync as a shorthand. """
        # spot is spot on viewport, not spot on grid?
        return (self.x, self.y)
    def draw(self, shift_x=0, shift_y=0):
        self.rect = pygame.Rect(
            (self.x - shift_x) * self.tile,
            self.edge + (self.y - shift_y) * self.tile + BoardState.offset(self.x) + 3,
            self.image.get_width(), self.image.get_height())
        self.text = font.render(self.shorthand(), True, Color("white"), Color("black"))        
        surf.blit(self.image, self.rect.midtop)        
        surf.blit(self.shield, self.rect.topright)
        surf.blit(self.text, self.rect.midtop)




class BoardState(ComputerAI):
    move_cost = {'p':2, 'm':11, 'h':4, 's':5, 'w':10, 'c':2, 'f':3}
    terrain_defense = {'p':1, 'm':1, 'h':1.1, 's':1.05, 'w':1, 'c':1.2, 'f':1}
    terrain_names = {'p':'plains', 'm':'mountain', 'h':'hills', 's':'swamp', 'w':'river', 'c':'castle', 'f':'forest'}

    def __init__(self, armies=None, **kwargs):
        super().__init__()
        self.board, self.board_width, self.board_height = make_board()
        self.board = add_river_and_castles(self.board)        
        self.view_port = (5,5) # 7 x 7 hex view
        self.view_margin = 2
        self.view_x_min = 0
        self.view_x_max = 4
        self.view_y_min = 0
        self.view_y_max = 4
        self.tile = 66
        self.edge = 33

        self.armies = []
        if not armies:
            self.army_spots = [(1,6), (4,4), (6,6)] # starting spots
            for _new in self.army_spots:
                #self.board[_new].army = Army(self.board, _new[0], _new[1], type=1, moves=6)
                #self.armies.append(self.board[_new].army)
                self.armies.append( Army(_new[0], _new[1], type=1, moves=6) )
        else:            
            for army in armies:
                self.armies.append( army )
                print(f"Adding {army.gen.name} {army.owner}")
        self.a = 0 # active army index        
        self.active_army = self.armies[self.a]
        self.active_spot = self.armies[self.a].spot() # start: location of first army

        for k,v in kwargs.items():
            setattr(self, k, v)

    def on_screen(self):
        return [piece for piece in self.board if (self.view_x_min <= piece[0] <= self.view_x_max) and (self.view_y_min <= piece[1] <=self.view_y_max)]
        
    @staticmethod
    def offset(x, tile=66):
        if x % 2 == 0:
            y_offset = int(0.5 * tile)
        else:
            y_offset = 0
        return y_offset
    
    def has_army(self, spot):
        for a in self.armies:
            if a.spot() == spot:
                return True
        return False
    def on_board(self, spot):
        return True if spot in self.board.keys() and spot in self.on_screen() else False
        
    def terrain_spot(self, spot):
        return self.board[spot].image_key # p m h s(wamp) f w 

    def move_army(self, keys):
        """Checks:
        [x] keys match allowed moves
        [x] new spot is not occupied
        [x] has enough movement points for terrrain
        [x] new spot is not off board
        - add all other possible move commands: attack, fire, mobilize, barricade, flee, view
        - add advanced: simult-attack, split/join, zoom map in/out, regroup
        - add attack for ranged units automatically expands possible squares with shaded overlay
        for arrows vs ballistas
        """
        x, y = self.active_spot
        delta = (0,0) # pass (dx, dy) into center_on()
        prv = False
        nxt = False
        if keys[pygame.K_7]:
            x -= 1
            if x % 2 == 0:
                y -= 1
                delta = (-1, -1)
            else:
                delta = (-1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_8]:
            y -= 1
            delta = (0, -1)
        elif keys[pygame.K_9]:
            x += 1
            if x % 2 == 0:
                y -= 1
                delta = (1, -1)
            else:
                delta = (1, 0)
        elif keys[pygame.K_1]:
            x -= 1
            if x % 2 != 0:
                y += 1
                delta = (-1, 1)
            else:
                delta = (-1, 0)
        elif keys[pygame.K_DOWN] or keys[pygame.K_2]:
            y += 1
            delta = (0, 1)
        elif keys[pygame.K_3]:
            x += 1
            if x % 2 != 0:
                y += 1
                delta = (1, 1)
            else:
                delta = (1, 0)
        elif keys[pygame.K_LEFT] or keys[pygame.K_4]:
            prv = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_6]:
            nxt = True
        elif keys[pygame.K_SPACE] or keys[pygame.K_5]:
            if self.active_army.moves_left >= self.active_army.moves:
                self.active_army.mobilize_points += 1 # LATER: reset to zero if move
                print(f"Mobility is now {self.active_army.moves + self.active_army.mobilize_points}")
            self.next_army()
            return True

        if not self.on_board((x,y)):
            print(f"invalid move")
            return False

        ##### DEBUG #####
        print(f"{self.active_spot} {self.terrain_names[self.terrain_spot(self.active_spot)]} moving onto {self.terrain_names[self.terrain_spot((x,y))]} {x,y}")

        # don't need movement points to attack
        if self.has_army((x,y)) and (x != self.active_spot[0] or y != self.active_spot[1]):
            this_army = [a for a in self.armies if a.spot() == (x,y)][0]
            if this_army.owner != 0:
                print(f"ATTACK {self.active_army.gen.war} vs {this_army.gen.war}")
                self.attack(this_army) # detached from self.armies?
                self.next_army()
                return False

        # compare next terrain and remaining movement points        
        terrain_cost = self.move_cost[self.board[(x,y)].image_key]
        moves_left = self.active_army.moves_left
        if terrain_cost > moves_left:
            print(f"{moves_left} = not enough movement left")
            return False

        
        # if move would be close to an edge, shift screen view
        ### TODO make it shift when moving NEAR edge (x-2) <= self.view_x_min
        """
        if (x == self.view_x_min or
            x == self.view_x_max or
            y == self.view_y_min or
            y == self.view_y_max):
            print('SHIFT VIEW', (x,y), self.view_x_min, self.view_x_max, self.view_y_min, self.view_y_max)
            # it can shift by both/either X,Y
            if x == self.view_x_min:
                self.shift_screen('x-1')
            if x == self.view_x_max:
                self.shift_screen('x+1')
            if y == self.view_y_min:
                self.shift_screen('y-1')
            if y == self.view_y_max:
                self.shift_screen('y+1')
        """

        # actually move piece
        if (self.on_board((x,y)) and
            self.has_army((x,y)) is False and
            (x != self.active_spot[0] or y != self.active_spot[1]) # x and/or y changed
            ):
            self.active_army.x = x
            self.active_army.y = y
            edge = 33
            tile = 66
            self.active_army.rect = pygame.Rect(self.active_army.x * tile, edge + self.active_army.y * tile + self.offset(self.active_army.x) + 3, self.active_army.image.get_width(), self.active_army.image.get_height())
            self.active_army.moves_left = moves_left - terrain_cost
            # update board_state now; draw army in new tile
            self.active_army.draw()
            # put terrain back on prev tile
            self.board[(self.active_spot[0], self.active_spot[1])].draw()
            self.active_army.mobilize_points = 0 # reset after moving any
            if not self.more_moves_possible():
                self.next_army()
            else:
                self.active_spot = (x,y)
            self.center_view_on(self.active_spot, delta)
            return True
        elif (x == self.active_spot[0] and y == self.active_spot[1]):
            return False # key pressed, but not an movement key
        elif self.has_army((x,y)) and (x != self.active_spot[0] or y != self.active_spot[1]):
            this_army = [a for a in self.armies if a.spot() == (x,y)][0]
            if this_army.owner == 0:
                print(f"invalid move")
                return False
        else:            
            return False
    def next_army(self):
        self.a += 1        
        if self.a > (len(self.armies)-1):
            print('next turn')
            self.a = 0
            # reset movement points for each army; adjust for saved mobilize points
            for a in range(len(self.armies)):
                self.armies[a].moves_left = self.armies[a].moves + self.armies[a].mobilize_points
        self.active_army = self.armies[self.a]
        self.active_spot = self.active_army.spot()
        
        
    def more_moves_possible(self):
        # checks for ANY possible movement to active_army's adjacent hexes
        (x,y) = (self.active_army.x, self.active_army.y)
        spot = self.active_spot
        moves_left = self.active_army.moves_left
        adjacent = [(x,y+1), (x+1,y), (x+1,y+1), (x-1,y), (x,y-1), (x-1,y-1)]
        for adj in adjacent:
            if self.board.get(adj) and self.move_cost[self.board[adj].image_key] <= moves_left:
                return True
        return False
    def attack(self, enemy):
        # TODO add enemy barricade defense 
        def_bonus = self.terrain_defense[self.terrain_spot(enemy.spot())]
        army_ratio = self.active_army.attack / enemy.defense
        war_ratio = (self.active_army.gen.war/enemy.gen.war)
        old_war_ratio = war_ratio
        if war_ratio > 1:
            war_ratio = war_ratio/(math.sqrt(war_ratio)) # approx divides by max 3
        elif war_ratio <= 1:
            war_ratio = math.sqrt(war_ratio)
        player_attack = war_ratio * army_ratio
        #print(f'calc: {war_ratio} * {def_bonus} * {army_ratio}') 
        enemy_defense = 1/player_attack * def_bonus
        total_loss = 1000 if self.active_army.gen.war > 50 else (600 + (self.active_army.gen.war/100)*400)
        # calc fraction of 640-800 or 1000 troops lost to each side
        player_loss = enemy_defense / (player_attack + enemy_defense) * total_loss
        enemy_loss = player_attack / (player_attack + enemy_defense) * total_loss
        # animate attack
        text1 = font.render(self.active_army.shorthand(), True, Color("white"), Color("black"))
        text2 = font.render(self.active_army.shorthand(), True, Color("black"), Color("white"))
        etext1 = font.render(enemy.shorthand(), True, Color("white"), Color("black"))
        etext2 = font.render(enemy.shorthand(), True, Color("black"), Color("white"))
        text3 = font.render(self.active_army.shorthand(), True, Color("black"), Color("red"))
        etext3 = font.render(enemy.shorthand(), True, Color("black"), Color("red"))
        clock = pygame.time.Clock()
        def animate(self, enemy, player0text, enemy1text):
            surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            surf.blit(self.active_army.shield, self.active_army.rect.topright)
            surf.blit(player0text, self.active_army.rect.midtop)
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(enemy1text, enemy.rect.midtop)
            clock.tick(16)
            pygame.display.flip()            
        for frame in range(8):
            animate(self, enemy, text1, etext2)
            animate(self, enemy, text2, etext1)
            animate(self, enemy, text3, etext1)
            animate(self, enemy, text1, etext3)
        self.active_army.size = max(self.active_army.size - player_loss, 0)
        enemy.size = max(enemy.size - enemy_loss, 0)
        self.active_army.draw()
        enemy.draw()
    def center_view_on(self, map_spot, delta):
        (x,y) = map_spot
        (dx, dy) = delta # immediately after moving piece, what xy changed?
        current_view_center = (self.view_x_min + self.view_margin, self.view_y_min + self.view_margin)
        print(f"delta spot: view_center: {current_view_center} | active_spot: {map_spot}")

        """# RECALL: x always gets -1 or +1, but y also gets -1 or +1 if x-column is ODD.        
        current_view_x_center = self.view_x_max - self.view_margin
        current_view_y_center = self.view_y_max - self.view_margin
        shift_x = x - current_view_x_center
        shift_y = y - current_view_y_center
        if shift_x < 0:
            shift_x = 0
        if shift_y < 0:
            shift_y = 0        
               
        if shift_x != 0:            
            self.view_x_min = (x-self.view_margin) if (x-self.view_margin) >= 0 else 0
            self.view_x_max = (x+self.view_margin) if (x+self.view_margin) <= self.board_width else self.board_width

        if shift_x < 0 and x % 2 == 0 and shift_y < 0:
            self.view_y_min = (y-self.view_margin) if (y-self.view_margin) >= 0 else 0
            self.view_y_max = (y+self.view_margin) if (y+self.view_margin) <= self.board_height else self.board_height
        else:
            if shift_x > 0 and shift_y >0:
                self.view_y_min = 1+ (y-self.view_margin) if (y-self.view_margin) >= 0 else 0
                self.view_y_max = 1+ (y+self.view_margin) if (y+self.view_margin) <= self.board_height else self.board_height
            if shift_x < 0 and :
                self.view_y_min = -1 + (y-self.view_margin) if (y-self.view_margin) >= 0 else 0
                self.view_y_max = -1 + (y+self.view_margin) if (y+self.view_margin) <= self.board_height else self.board_height
            if shift_x == 0:
                self.view_y_min = (y-self.view_margin) if (y-self.view_margin) >= 0 else 0
                self.view_y_max = (y+self.view_margin) if (y+self.view_margin) <= self.board_height else self.board_height
        """
        if (dx + self.view_x_min) >= 0:
            self.view_x_min += dx
        if (dx + self.view_x_min) <= self.board_width:
            self.view_x_max += dx
        if (dy + self.view_y_min) >= 0:
            self.view_y_min += dy
        if (dy + self.view_y_min) <= self.board_height:
            self.view_y_max += dy
        print(f"dxdy ({dx}, {dy}) current xy {(x,y)} shifted xy_min {(self.view_x_min, self.view_y_min)}")
        # NEXT: shift the army position opposite of board-shift to compensate
        self.draw_map(self.view_x_min, self.view_y_min)

    def draw_map(self, shift_x=0, shift_y=0):
        for piece in self.on_screen():
            (x,y) = piece
            cam_x = x - self.view_x_min
            cam_y = y - self.view_y_min
            surf.blit(self.board[piece].image, (self.edge + (cam_x*self.tile), self.offset(cam_x) + self.edge + (cam_y*self.tile)))
        [a.draw(shift_x, shift_y) for a in self.armies]
        pygame.display.flip()


def game_loop():
    clock = pygame.time.Clock()
    screen.fill(BACKGROUND)
    bs = BoardState(armies=create_armies()) # makes board; adds default armies
    bs.draw_map()
    #cursor = ActiveCursor(*bs.active_spot)
    [a.draw() for a in bs.armies]

    while True:
        #cursor.draw(screen)
        pygame.display.flip()
        clock.tick(60)        
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and sum(keys) > 0:                
                successful = bs.move_army(keys)
                #cursor.update(bs.active_spot)
                #cursor = ActiveCursor(*bs.active_spot)
        if bs.active_army.owner != 0:
            print(f"Enemy: {bs.active_army.gen.name}'s turn:")
            # ADD AI MOVE FUNC HERE
            bs.AI_move()
            bs.next_army()
            cursor.update(bs.active_spot)
                
                
if __name__ == "__main__":
    game_loop()
