# Qin Kingdoms 2023

""" TODOs:
[x] 1. random map generator
[x] 2. attach unit info to board (not maphex); allow movement
[x] 3. add multiple armies; allow movement
[x] 4. add generals to armies; count movement points; next army only after finished moving;
[x] 5. mobilize works; player shields
[x] 5. added forests; add enemy armies; basic attacking/defending
[-] 6. add castles

- add ranged attacks
- show error messages on screen, not just print()
- make larger map in memory (board dict), allow scrolling
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
import math
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
with open('warlords.txt','r') as f:
    NAMES = f.read().split('\n')
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surf = pygame.display.get_surface()
board_segs = pygame.sprite.Group()
#pygame.key.set_repeat(100, 100) --- used in games where you hold-down a key to keep moving, not this game.
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
    last_piece_positions = {'p':0, 'm':1, 'h':2, 's':3, 'w':4, 'c':5, 'f':6}
    weights = [30, 12, 12, 10, 0, 0, 15]
    board = {}    
    for xx in range(10):
        for yy in range(7):
            y_offset = offset(xx)
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
            piece.draw()
            board[(xx, yy)] = piece
    return board

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

def create_armies():
    armies = [] # list of Army objects with Generals
    army_spots = [(1,6), (4,4), (6,6)] # starting spots
    enemy_spots = [(8,3), (6,4)]
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

def random_shield():
    raw = SpriteSheet("sheet-crests-28.jpg")
    rects = []
    for x in range(8):
        for y in range(8):
            rects.append((28*x, 28*y, 28, 28))
    images = raw.images_at(rects)
    return random.choice(images)     

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

class General():
    specialties = [
        0,1,2,3,4,5,6, # unit types
        'naval',
        'fire',
        # mobilize and barricade -- cannot specialize, always +1, max +2 defense and max 10 mobility.
        'recruiting',
        'cultivation',
        'culture',
    ]
    def __init__(self):
        self.name = f"{random.choice(NAMES)} {random.choice(NAMES)}"
        # randomly generate scores
        self.war = random.randrange(10,99)
        self.int = random.randrange(10,99)
        self.cha = random.randrange(10,99) # charm, not charisma, in this world
        self.specialty = random.choice(self.specialties)

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
    def __init__(self, xx, yy, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        for key,val in kwargs.items():
            setattr(self, key, val)
        if not hasattr(self, 'gen'):
            self.gen = General() # creates new general; adds war, int, cha, etc to army.gen
        self.xx = xx
        self.yy = yy
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
        edge = 33
        tile = 66
        self.rect = pygame.Rect(self.xx*tile, edge + self.yy*tile + offset(self.xx) + 3, self.image.get_width(), self.image.get_height())        
    def shorthand(self):
        return str(int(self.size / 100))
    def spot(self):
        """ must be dynamic, not attribute, & recalculated each time to remain in sync as a shorthand. """
        return (self.xx, self.yy)
    def draw(self):
        self.text = font.render(self.shorthand(), True, Color("white"), Color("black"))        
        surf.blit(self.image, self.rect.midtop)        
        surf.blit(self.shield, self.rect.topright)
        surf.blit(self.text, self.rect.midtop)



class SpriteSheet(object):
    # ref: https://www.pygame.org/wiki/Spritesheet
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except (pygame.error, message) :
            print('Unable to load spritesheet image:', filename)
            raise (SystemExit, message)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class ComputerAI():
    def __init__(self):
        pass
    def AI_choose_action(self):
        pass
    def AI_move(self):
        # point towards nearest enemy with less troops, and find fastest path there.        
        pass

class BoardState(ComputerAI):
    move_cost = {'p':2, 'm':11, 'h':4, 's':5, 'w':10, 'c':2, 'f':3}
    terrain_defense = {'p':1, 'm':1, 'h':1.1, 's':1.05, 'w':1, 'c':1.2, 'f':1}

    def __init__(self, armies=None, **kwargs):
        super().__init__()
        self.board = make_board()
        self.board = add_river(self.board)
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
        #self.armies = [v.army for spot,v in self.board.items() if hasattr(v,'army')]
        self.a = 0 # active army index        
        self.active_army = self.armies[self.a]
        self.active_spot = self.armies[self.a].spot() # start: location of first army
        for k,v in kwargs.items():
            setattr(self, k, v)
    def has_army(self, spot):
        for a in self.armies:
            if a.spot() == spot:
                return True
        return False
    def on_board(self, spot):
        return True if spot in self.board.keys() else False
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
        elif keys[pygame.K_SPACE] or keys[pygame.K_5]:
            if self.active_army.moves_left >= self.active_army.moves:
                self.active_army.mobilize_points += 1 # LATER: reset to zero if move
                print(f"Mobility is now {self.active_army.moves + self.active_army.mobilize_points}")
            self.next_army()
            return True

        if not self.on_board((x,y)):
            print(f"invalid move")
            return False

        # don't need movement points to attack
        if self.has_army((x,y)) and (x != self.active_spot[0] or y != self.active_spot[1]):
            this_army = [a for a in self.armies if a.spot() == (x,y)][0]
            if this_army.owner != 0:
                print("ATTACK")
                self.attack(this_army) # detached from self.armies?
                self.next_army()
                return False

        # compare next terrain and remaining movement points        
        terrain_cost = self.move_cost[self.board[(x,y)].image_key]
        moves_left = self.active_army.moves_left
        if terrain_cost > moves_left:
            print(f"{moves_left} = not enough movement left")
            return False

        if (self.on_board((x,y)) and
            self.has_army((x,y)) is False and
            (x != self.active_spot[0] or y != self.active_spot[1])
            ):
            self.active_army.xx = x
            self.active_army.yy = y
            edge = 33
            tile = 66
            self.active_army.rect = pygame.Rect(self.active_army.xx*tile, edge + self.active_army.yy*tile + offset(self.active_army.xx) + 3, self.active_army.image.get_width(), self.active_army.image.get_height())
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
        self.active_spot = (self.armies[self.a].xx, self.armies[self.a].yy)
    def more_moves_possible(self):
        # checks for ANY possible movement to active_army's adjacent hexes
        (x,y) = (self.active_army.xx, self.active_army.yy)
        spot = self.active_spot
        moves_left = self.active_army.moves_left
        adjacent = [(x,y+1), (x+1,y), (x+1,y+1), (x-1,y), (x,y-1), (x-1,y-1)]
        for adj in adjacent:
            if self.board.get(adj) and self.move_cost[self.board[adj].image_key] <= moves_left:
                return True
        return False
    def attack(self, enemy):
        # calculate ratios, then divide 1000 troops lost by the ratio
        # ratio (war2/war1 for 0.1 to 9.9 range) * hill or castle terrain defense [+ barricade]
        # + (attack power / defense toughness)
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
        #print(self.active_army.gen.war, enemy.gen.war, old_war_ratio, '-->', war_ratio)
        #print(f'calc: {war_ratio} * {def_bonus} * {army_ratio}') 
        enemy_defense = 1/player_attack * def_bonus
        total_loss = 1000 if self.active_army.gen.war > 50 else (600 + (self.active_army.gen.war/100)*400)
        # calc fraction of 640-800 or 1000 troops lost to each side
        player_loss = enemy_defense / (player_attack + enemy_defense) * total_loss
        enemy_loss = player_attack / (player_attack + enemy_defense) * total_loss
        #print(round(player_attack,2), round(enemy_defense,2), int(player_loss), int(enemy_loss))
        # animate attack
        text1 = font.render(self.active_army.shorthand(), True, Color("white"), Color("black"))
        text2 = font.render(self.active_army.shorthand(), True, Color("black"), Color("white"))
        etext1 = font.render(enemy.shorthand(), True, Color("white"), Color("black"))
        etext2 = font.render(enemy.shorthand(), True, Color("black"), Color("white"))
        text3 = font.render(self.active_army.shorthand(), True, Color("black"), Color("red"))
        etext3 = font.render(enemy.shorthand(), True, Color("black"), Color("red"))
        clock = pygame.time.Clock()
        for frame in range(8):
            surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            surf.blit(self.active_army.shield, self.active_army.rect.topright)
            surf.blit(text1, self.active_army.rect.midtop)
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(etext2, enemy.rect.midtop)
            clock.tick(16)
            pygame.display.flip()
            surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            surf.blit(self.active_army.shield, self.active_army.rect.topright)
            surf.blit(text2, self.active_army.rect.midtop)
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(etext1, enemy.rect.midtop)
            clock.tick(16)
            pygame.display.flip()
            surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            surf.blit(self.active_army.shield, self.active_army.rect.topright)
            surf.blit(text3, self.active_army.rect.midtop)
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(etext1, enemy.rect.midtop)
            clock.tick(16)
            pygame.display.flip()
            surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            surf.blit(self.active_army.shield, self.active_army.rect.topright)
            surf.blit(text1, self.active_army.rect.midtop)
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(etext3, enemy.rect.midtop)
            clock.tick(16)
            pygame.display.flip()
        self.active_army.size = max(self.active_army.size - player_loss, 0)
        enemy.size = max(enemy.size - enemy_loss, 0)
        self.active_army.draw()
        enemy.draw()        


def game_loop():
    clock = pygame.time.Clock()
    screen.fill(BACKGROUND)
    bs = BoardState(armies=create_armies()) # makes board; adds default armies    
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
                successful = bs.move_army(keys)
                cursor.update(bs.active_spot)
        if bs.active_army.owner != 0:
            print(f"Enemy: {bs.active_army.gen.name}'s turn:")
            # ADD AI MOVE FUNC HERE
            bs.AI_move()
            bs.next_army()
            cursor.update(bs.active_spot)
                
                
if __name__ == "__main__":
    game_loop()
