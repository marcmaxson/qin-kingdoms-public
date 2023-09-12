# Qin Kingdoms 2023

# for android 
#try:
#    import pygame_sdl2
#    pygame_sdl2.import_as_pygame()
#except ImportError:
#    print("sdl2 not working")

""" TODOs:
[x] 1. random map generator
[x] 2. attach unit info to board (not maphex); allow movement
[x] 3. add multiple armies; allow movement
[x] 4. add generals to armies; count movement points; next army only after finished moving;
[x] 5. mobilize works; player shields; added forests; add enemy armies; basic attacking/defending
[x] 6. subtract troops from attacks;
[x] 7. add castles (a random number, centralized, and adjacent to each other)
[x] 7. [took 1 week] any size board supported with scrolling
        allow screen to scroll when unit moves close to edge
[x] 7. put cursor and armies back on board
[x] 7. place enemy on castles to start

[x] 8. shift view to active army
[x] 8. prevent starting squares from being in water/mtn
[x] 8. ENEMY AI; path_to_enemy; finds nearest_enemy_army
        ignores mountains and accounts for terrain types in shortest path
        finds weakest enemy (calculates power ratio and sorts); choose attack/defend/range
[x] 8. moves towards best enemy to attack; attacks adjacent enemies; self.is_adjacent works!
[x] 9. basic side message console (vanilla, not using pygame-gui yet)

[x] 10. (Monday July 24, 2023)
        capture army works - moves to self.dead_armies
        enemies still not moving towards army well yet.
        self.menu_display - useful and versatile message function for all combat stuff.
        mobilize is not storing movement. Only +1 gets saved for human moves, but the console shows all saved movement.
        (might be same for AI)
        most messages are in console now.
        end of turn bug fixed (centers on new army)
        AI army blocked (add square into game grid and recalculate
        FIXED bug: FIRST time you move first army, background overwrites army; fix with enemy moving first?
        Fixed bug: enemy army can always attack me if left-1 and up-2; x is even.
        from enemy (6,3) attacking (5,2); so (6,3) is NOT next to (5,2) e.g. x-1, y-1 when x % 2 == 0
        also: (8, 7) to (7, 6) movement was 2 hexes (x-1, y-1) on even x-row.
        also: (10, 6), (11, 5) up+right on even row
        likely fixed: if enemy path crosses water, enemy doesnt store up movement points to cross        
        added (V)IEW MODE -(sub-loop where keys respond but locks out all other moves until ESC)

[x] 11. detects 2 hexes away consistently (for ranged attack)
        shows targeted hexes on screen, with specific army shown
        FUTURE: [TAB]: changes target -- not quite yet
        (r)anged attack works!
        FUTURE: move the "two_away()" function to return those spots, so enemy AI can know it is in range.
        FUTURE: animate volley of arrows from army to army        
[x] 12. battle ends with win/loss conditions (time up, armies defeated, all castles occupied)
        add +naval bonus; you lost worked;
        ComputerAI has a working three_hexes_away map (for ballistas)

[x] 13. detects mouse clicks on board; converts to screen hex position.
        ballistas work (3 hexes away)
        barricade (pikemen bonus)
        forest range defense bonus
        randomness to ranged attack results
        changed generals to 25-99 range instead of 10-99 range for abilities
        fix AI: blocked by other army (recalcs and goes around)
        view mode: shows army stats under cursor
        display possible move keys below army
        works: actually test all_castles_filled, all invaders dead
        AI: if range attack, use it instead of regular attack
        AI: only regular attack once
        Check castles only at end of turn
        FINALLY FIXED the first turn cursor bug!
        range attack bug: if off screen, scroll to them first.
[x] 14. mouse/touch control movement
        make 2-min demo video with loom
        mouse/touch side menu buttons
        refactor code army.owner != instead of 0 vs 1 (so 2,3,4 etc will work)
        mouseover hightlight buttons
        battle_test_AI -- calls game_loop with 2 computer players, and game runs!
        battle_test_AI.py -- able to watch game play at 100X speed and log results!
[x] 15. tracking win/loss data in log; fixing various AI bugs that broke game.
        bug: 21 days are up is always the end condition. did not exit when finds no army left.
        add experience at end of battle, to help with calculating best/worst styles
            experience is divided among all surviving generals of winning side, and is
            exp = (net troop loss / 10); or if a draw (sum troop loss/4) per army

[x] 16. plot results of 120 battles
        AI_level 3 options (player level difficulty)
        Track AI test options for plots
        have plotter show "test note" separately - works! And proves barricade improves def win rate 3X.
[x] 17. computerAI: range, backup
        I THINK I FIXED BUGS:
        DEF heavy infantry 5/5 with 100 troops not attacking anybody, just sits on castle
        despite being the biggest army. Does not attack adjacent either (lvl 4)
        DEF (level 4) infantry and militia not attacking me (from castle)
        DEF archers moved right next to my army instead of stopped 2 away
        DEF 5/2 calv did not engage any troops (level 4)
        FIX: if total friend army size is larger than enemy, AND
        another friend army is nearby,
        go ahead and engage the closest enemy (more aggressively):
        because two or littler armies will beat one larger one. current DEF AI waits
        if each army is weaker than the one invader.
        made archers 2/2 instead of 2/3
        ADDED: General's specialty adds +1 to attack, or if pikemen, +1 to defense, or if range, +1 range attack,
        if unit type matches their specialty type
        BUG -- battle_test: when armies are exactly even, nobody attacks
        (not a problem with lvl 1 (brute force))

BUG: I have one army left, but game keeps skipping it's move.
BUG: Why does it spin wheels when army is captured. Next turn function seems to have a slow step?

Add - if two foe armies nearby, move towards the weaker one
(a genetic algo step; not always the best move, but leads to more strategies)
Add - Pikemen: move between archer and army and barricade. (lvl5)

- AI: hide behind army or with mountains between army and enemy
- AI: if range and blocked, don't pass, move towards allied army instead


- add fire
- add loyalty (and switching)
- add rice (lvl5 DEF)
    - move towards rice, if rice unguarded
- lvl 5: set fire, if outnumbered
- lvl 6: move away from enemies, if outnumbered and more castles than can be occupied

- add mouse and fingerdown/fingerup/fingermotion tablet support
- range [TAB] to change target 
- toggle tileset from retro NES to modern tiles to cartoonish tiles
- captured generals: add to Player class for (main game state)
    - future: option to redeploy captured generals with 100 men on board (taken from army that defeated it)
    - add warning if loyalty is below 40
- linear interpolation when scrolling
- ??? for large maps, use random seed terrain types and grow the pieces around them,
- future, harder: split to defend archers from enemy
"""
import math
import time
import random
import sys
import pygame
from pygame import Color
from game_classes import (
    ComputerAI, SpriteSheet,
    random_shield, SideMenu,
    ActiveCursor, General
)
from collections import Counter

DEBUG = False
HEIGHT = 600
WIDTH = 800
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
msgs = pygame.Surface((200, HEIGHT))

# TODO: these are in BoardState, for ComputerAI; refer to them with self. everywhere.
surf = pygame.display.get_surface()
font = pygame.font.Font('freesansbold.ttf', 28)
clock = pygame.time.Clock()

images = {
    'p': pygame.image.load("tile-plains.png").convert(),
    'm': pygame.image.load("tile-mtn.png").convert(),
    'h': pygame.image.load("tile-hills.png").convert(),
    's': pygame.image.load("tile-swamp.png").convert(),
    'w': pygame.image.load("tile-water.png").convert(),
    'c': pygame.image.load("tile-castle.png").convert(),
    'f': pygame.image.load("tile-forest.png").convert(),
}
target = pygame.image.load("tile-target.png").convert()
target.set_colorkey((0,0,0))
target2 = pygame.image.load("tile-target-02.png").convert()
target2.set_colorkey((0,0,0))
extra_images = {
    'a': pygame.image.load("tile-army.png").convert(),
    'f1': pygame.image.load("tile-fire-01.png").convert(),
    'f2': pygame.image.load("tile-fire-02.png").convert(),
    'f3': pygame.image.load("tile-fire-03.png").convert(),
    't': target,
    't2': target2,
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
        self.edge = 33        
    def draw(self, shift_x=0, shift_y=0):
        # WIDTH, HEIGHT, BOX_WIDTH, BOX_HEIGHT -- this is rarely called, like when an army is captured
        self.rect = pygame.Rect(self.edge + self.pixelx - (66*shift_x),
                                self.edge + self.pixely - (66*shift_y),
                                self.image.get_width(),
                                self.image.get_height())
        surf.blit(self.image, self.rect.topleft)
        pygame.display.flip()

def make_board(width=24, height=24):
    tile = 66
    last_piece_type = None
    last_piece_positions = {'p':0, 'm':1, 'h':2, 's':3, 'w':4, 'c':5, 'f':6}
    weights = [50, 12, 12, 10, 0, 0, 10] 
    unique_tile = random.choice(['s','f'])
    if unique_tile == 's':
        weights[3] = 20
        weights[6] = 0
    elif unique_tile == 'f':
        weights[3] = 0
        weights[6] = 20
    def is_adj(this_spot, that_spot):
        (x,y) = this_spot
        (x2, y2) = that_spot
        # 7-24-23: looks like up+left and up+right have reversed signs
        if (x-1) == x2 and (x % 2 != 0) and (y-1) == y2:
            return True # up and left
        elif (x-1) == x2 and (x % 2 == 0) and (y == y2):
            return True # up and left
        elif (x == x2) and (y-1) == y2:
            return True # up
        elif (x+1) == x2 and (x % 2 != 0) and (y-1) == y2: # up and right
            return True
        elif (x+1) == x2 and (x % 2 == 0) and (y == y2): # up and right
            return True
        elif (x-1) == x2 and (x % 2 == 0) and (y+1) == y2: # down and left
            return True
        elif (x-1) == x2 and (x % 2 != 0) and (y == y2): # down and left
            return True
        elif (x == x2) and (y+1 == y2):
            return True # down
        elif (x+1) == x2 and (x % 2 == 0) and (y+1) == y2: # down and right
            return True
        elif (x+1) == x2 and (x % 2 != 0) and (y == y2): # down and right
            return True
        return False # none of these are True        
        
    board = {}    
    for xx in range(width):
        for yy in range(height):
            y_offset = BoardState.offset(xx)
            x = (xx * tile)
            y = int((yy * tile) + y_offset)

            # picking terrain type
            tiles = list(images.keys())            
            if last_piece_type:                
                weights[last_piece_positions[last_piece_type]] = 60
            adjacent_tiles = [(xx, yy+1), (xx, yy-1), (xx-1, yy-1), (xx-1, yy+1), (xx+1, yy), (xx-1, yy), (xx+1, yy+1), (xx+1,yy-1)]
            for adj in adjacent_tiles:
                if board.get(adj) and is_adj((xx,yy), adj):
                    temp = last_piece_positions[board[adj].image_key]
                    weights[temp] += 15
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
    # add more plains in spots
    for test in range(12): # pick 12 random spots
        (xx,yy) = (random.choice(range(*x_range)), random.choice(range(*y_range)))
        if not board.get((xx,yy)):
            continue
        adjacent_tiles = [(xx, yy+1), (xx, yy-1), (xx-1, yy-1), (xx-1, yy+1), (xx+1,yy), (xx-1,yy), (xx+1,yy+1), (xx+1,yy-1)]
        for adj in adjacent_tiles:
            if board.get(adj):
                if board[adj].image_key not in ('w','c'):
                    board[adj].image_key = 'p'
                    board[adj].image = images['p']

    # RIVER
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
    num_castles = random.choice([1,2,3,3,3,3,4,4,4,4,5,5,5,6,6,7,8])
    img_castle = 'c'
    (xx, yy) = random.choice([8,9,10,11,12]), random.choice([5,6,7,8,9]) #(int(x_range[1]/2), int(y_range[1]/2))
    used_spots = []
    for n in range(num_castles):
        y_offset = BoardState.offset(xx)
        x = (xx * tile)
        y = int((yy * tile) + y_offset)
        board[(xx, yy)] = MapHex(img_castle, x, y, xx, yy)
        used_spots.append((xx, yy))
        while True:
            adjx = random.choice([1,0,-1])
            adjy = random.choice([1,0,-1])
            if (xx + adjx, yy + adjy) not in used_spots and (adjx != adjy):
                xx += adjx
                yy += adjy
                break            
    return board

def create_armies(board):
    armies = [] # list of Army objects with Generals
    army_spots = [(2,2), (0,1), (5,3), (3,4)] # starting spots
    enemy_spots = [(8,8), (9,9), (10,9), (8,9)] # these get moved to castles, if possible
    player_shield = random_shield()
    enemy_shield = random_shield()
    if player_shield == enemy_shield:
        enemy_shield = random_shield()
    occupied_spots = []
    for spot in army_spots:
        # no armies start on mountains or rivers
        if board[spot].image_key in ('w','m'):
            (xx,yy) = spot
            adjacent_tiles = [(xx, yy+1), (xx, yy-1), (xx-1, yy-1), (xx-1, yy+1), (xx+1, yy+1), (xx+1, yy), (xx-1, yy)]
            tries = 0
            while True:
                adj = random.choice(adjacent_tiles)
                if not board.get(adj):
                    continue
                if board[adj].image_key not in ('w','m') and adj not in occupied_spots:
                    spot = adj
                    occupied_spots.append(spot)
                    break
                tries +=1
                if tries > 10:
                    print(f"ERROR, could not move spot off {board[spot].image_key}")
                    break
        army = Army(spot[0], spot[1],
                    type=random.randrange(0,9), owner=0,
                    size=random.choice([1333, 2666, 2400, 3100, 5500, 7850, 10100]),
                    shield=player_shield)
        armies.append( army )
    castle_spots = [spot for spot in board if board[spot].image_key == 'c']
    occupied_castles = []
    for spot in enemy_spots:
        # place each army on a castle, unless all castles are occupied
        avail_castles = list(set(castle_spots) - set(occupied_castles))
        while True:
            if len(avail_castles) > 0:
                spot = random.choice(avail_castles)
            else:
                while True:
                    spot = (random.choice([7,8,9,10]), random.choice([5,6,7,8]))
                    if spot in occupied_castles:
                        print(f"WARNING: duplicate enemy placement on board: {spot}")
                    else:
                        break
            if spot not in occupied_castles:
                occupied_castles.append(spot)
                break
        # TODO: check that enemy armies don't occupy same spots
        army = Army(spot[0], spot[1],
                    type=random.randrange(0,9), owner=1,
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
        4:2, 5:2, 6:1, 7:2, 8:3, 9:1, 11:5, 12:1,
    }
    range_attacks = {
        4:2, 6:4, 7:2, 8:4
    }
    unit_moves = {
        0:6, 1:6, 2:6, 3:6, 4:6, 5:8, 6:4, 7:8, 8:6,
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
            self.owner = 0 # human; 1 = enemy defender; 2 = enemy attacker
        if not hasattr(self, 'size'):
            self.size = 1000
        if not hasattr(self, 'shield'):
            self.shield = random_shield()
        self.attack = self.attacks[self.type]
        self.defense = self.defenses[self.type]
        self.range_attack = self.range_attacks.get(self.type, 0)
        self.moves_left = self.moves
        self.mobilize_points = 0
        self.barricade_points = 0
        self.image = extra_images['a']
        self.image_key = 'a'
        self.edge = 33
        self.tile = 66
        self.rect = pygame.Rect(self.x*self.tile, self.edge + self.y*self.tile + BoardState.offset(self.x) + 3, self.image.get_width(), self.image.get_height())
    def shorthand(self):
        return str(math.ceil(self.size / 100))
    def spot(self):
        """ must be dynamic, not attribute, & recalculated each time to remain in sync as a shorthand. """
        # spot is spot on viewport, not spot on grid?
        return (self.x, self.y)
    def strength(self):
        unit_pow = (self.attacks[self.type] + self.defenses[self.type])/2
        return int( (self.gen.war/10) * unit_pow * (self.size/100) )
    def draw(self, shift_x=0, shift_y=0):
        self.rect = pygame.Rect(
            (self.x - shift_x) * self.tile,
            self.edge + (self.y - shift_y) * self.tile + BoardState.offset(self.x) + 3,
            self.image.get_width(), self.image.get_height())
        self.text = font.render(self.shorthand(), True, Color("white"), Color("black"))        
        surf.blit(self.image, self.rect.midtop)        
        surf.blit(self.shield, self.rect.topright)
        surf.blit(self.text, self.rect.midtop)




class BoardState(ComputerAI, SideMenu):
    move_cost = {'p':2, 'm':11, 'h':4, 's':5, 'w':10, 'c':2, 'f':3}
    terrain_defense = {'p':1, 'm':1, 'h':1.1, 's':1.05, 'w':1, 'c':1.2, 'f':1}
    # forest range defense 1.25 handled in self.range_attack()
    terrain_names = {'p':'plains', 'm':'mountain', 'h':'hills', 's':'swamp', 'w':'river', 'c':'castle', 'f':'forest'}
    map_panes = { # xmin, xmax, ymin, ymax -- where max is hex that shifts view
        (0,0): (0, 6, 0, 6),
        (1,0): (4, 10, 0, 6),
        (2,0): (8, 14, 0, 6),
        (3,0): (12, 18, 0, 6),
        (0,1): (0, 6, 4, 10),
        (1,1): (4, 10, 4, 10),
        (2,1): (8, 14, 4, 10),
        (3,1): (12, 18, 4, 10),        
        (0,2): (0, 6, 8, 14),
        (1,2): (4, 10, 8, 14),
        (2,2): (8, 14, 8, 14),
        (3,2): (12, 18, 8, 14),
        (0,3): (0, 6, 12, 18),
        (1,3): (4, 10, 12, 18),
        (2,3): (8, 14, 12, 18),
        (3,3): (12, 18, 12, 18),        
    }

    def __init__(self, armies=None, **kwargs):
        self.board, self.board_width, self.board_height = make_board()
        self.board = add_river_and_castles(self.board)
        self.pane = (0,0)
        self.view_port = (7,7) # 7 x 7 hex view
        self.view_margin = 3
        self.view_x_min = 0
        self.view_x_max = 6
        self.view_y_min = 0
        self.view_y_max = 6
        self.tile = 66
        self.edge = 33
        self.font = font
        self.font_sm = pygame.font.Font('freesansbold.ttf', 20)
        self.font_banner = pygame.font.Font(pygame.font.get_default_font(), 80)
        self.surf = surf
        self.clock = clock
        self.menu_last_row = 0
        self.BACKGROUND = (20, 20, 20)
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
        self.turn = 1
        self.last_turn = 21
        self.wait = 1 # 100 to speed up AI games; longer to increase waits
        self.game_end = None # tracking for AI learning
        self.menu_buttons = []
        super().__init__()

        self.armies = []
        self.dead_armies = []
        if not armies:
            self.army_spots = [(1,1)] # starting spot
            for _new in self.army_spots:
                self.armies.append( Army(_new[0], _new[1], type=1, moves=6) )
        else:            
            for army in armies:
                self.armies.append( army )
                print(f"Adding {army.gen.name} {army.owner}")
        self.a = 0 # active army index        
        self.active_army = self.armies[self.a]
        self.active_spot = (0,0) # self.armies[self.a].spot() # start: location of first army; gets updated after create_armies
        self.cursor = ActiveCursor(*self.active_spot)
        self.players_AI_level = {0:0, 1:1, 2:1}
        self.DEBUG_every_army_moved = []
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

    def get_spot_clicked(self, mouse_pos):
        """ for mouse or touchscreens; returns spot on board or button clicked """
        (mouse_x, mouse_y) = mouse_pos
        # first, check if menu button clicked
        if hasattr(self, 'menu_buttons') and isinstance(self.menu_buttons, list):
            for (button,action,menutext,hovering) in self.menu_buttons: # list of pairs
                if button.collidepoint(mouse_pos):
                    return action

        # next, if on game board, return board (x,y)
        board_x = (mouse_x - self.edge)/self.tile
        board_x = None if (board_x < 0 or board_x > 7) else int(board_x)
        if board_x is None:
            return None
        if board_x % 2 == 0:
            board_y = (mouse_y - self.tile)/self.tile
        else:
            board_y = (mouse_y - self.edge)/self.tile
        board_y = None if (board_y < 0 or board_y > 7) else int(board_y)
        if board_y is None:
            return None
        return (int(board_x), int(board_y))

    def move_army_by_mouse_touch(self, click_spot):
        click_spot = (click_spot[0] + self.view_x_min, click_spot[1] + self.view_y_min)
        # center on piece
        if not self.on_board(click_spot):
            # shift view to active unit
            if click_spot in self.board:
                self.shift_map_pane()            
            else:
                self.menu_display(f"Invalid move")
                print(f"DEBUG MOUSE [not on board] active_spot {self.active_spot} ... {self.active_army.spot()}")
                return False
        
        # MOVE OK?
        if (self.is_adjacent(click_spot) and # to self.active_army.spot()
            self.on_board(click_spot) and
            not self.has_army(click_spot)
            ):

            # compare next terrain and remaining movement points        
            terrain_cost = self.move_cost[self.board[click_spot].image_key]
            # adjust for +naval
            if self.board[click_spot].image_key == 'w' and self.active_army.gen.specialty == 'naval':
                terrain_cost = 6            
            moves_left = self.active_army.moves_left
            if terrain_cost > moves_left:
                if self.board[click_spot].image_key == "m":
                    self.menu_display(f"Cannot cross mountains.", "Yellow", ephemeral=True)
                else:
                    self.menu_display(f"That move costs ({terrain_cost} vs {moves_left})", "Yellow", ephemeral=True)
                return False

            # actually move piece
            self.active_army.x = click_spot[0]
            self.active_army.y = click_spot[1]
            self.active_army.moves_left = moves_left - terrain_cost
            self.active_army.mobilize_points = 0 # reset after moving
            self.active_army.barricade_points = 0 # rest after moving
            if not self.more_moves_possible():
                self.next_army()
            else:
                self.active_spot = click_spot            
            self.shift_map_pane()
            return True
            
        # Attack!
        if self.has_army(click_spot) and self.is_adjacent(click_spot):
            this_army = [a for a in self.armies if a.spot() == click_spot][0]
            if self.active_army.owner == this_army.owner:
                return False
            war_ratio = (self.active_army.attack*self.active_army.gen.war) / (1+ (this_army.attack*this_army.gen.war))
            advantage = self.active_army.gen.name if war_ratio > 1 else this_army.gen.name
            self.menu_display([f"{self.active_army.gen.name} attacking",
                               f"{this_army.gen.name}",
                               f"Might {self.active_army.attack} vs {this_army.defense}",
                               f"Leaders {self.active_army.gen.war} vs {this_army.gen.war}",
                               f"Advantage: {self.active_army.gen.name}",
                               ], "red", replace=True)
            self.attack(this_army) # detached from self.armies?                
            self.next_army()
            self.shift_map_pane()
            return False

        self.menu_display(f"Invalid move", ephemeral=True)
        #print(f'move failed: mouse {click_spot} | active {self.active_spot}')

    def menu_button_actions(self, action):
        #print('menu button', action) # ['A', 'S', 'R', 'B', 'V'] where "A"rrow keys do nothing.
        if action == 'A':
            self.menu_display(["Move: click on","spot next to army"], ephemeral=True)
        elif action == 'S':
            if self.active_army.moves_left >= self.active_army.moves:
                self.active_army.mobilize_points += 1 # LATER: reset to zero if move
                self.menu_display(f"Mobility is now {self.active_army.moves + self.active_army.mobilize_points}")
            self.next_army()
            self.shift_map_pane()
        elif action == 'R':
            if self.active_army.range_attack > 0:
                self.range_attack()
                self.next_army()
                self.shift_map_pane()
                self.cursor.update(self.active_spot, self.view_x_min, self.view_y_min)
                return
            else:
                self.menu_display("Not a ranged unit", ephemeral=True)
        elif action == 'B':
            if self.active_army.type == 3 and self.active_army.barricade_points < 2:
                self.active_army.barricade_points += 1
            elif self.active_army.barricade_points > 0:
                self.menu_display(["Barricade defense",f"already max: {self.active_army.barricade_points + self.active_army.defense}"], ephemeral=True)
                return
            else:
                self.active_army.barricade_points += 1
            def_lvl = self.active_army.barricade_points + self.active_army.defense
            self.menu_display(f"Barricade: Defense now {def_lvl}","Wheat", wait=2)            
            self.next_army()
            self.shift_map_pane()
        elif action == 'V':
            self.view_mode()
            
    def move_army(self, keys, mouse_pos=None):
        """
        Checks:
            [x] keys match allowed moves
            [x] new spot is not occupied
            [x] has enough movement points for terrrain
            [x] new spot is not off board
        Moves:
            [x] attack, [x] mobilize, [x] view [x] range_attack [x] barricade
            [x] shows attack for ranged units - possible squares
        - add all other possible move commands: flee, fire        
        - add advanced moves: simult-attack, split/join, zoom map in/out, regroup
        """
        if mouse_pos: # works, but not implemented yet
            click_spot = self.get_spot_clicked(mouse_pos)
            if isinstance(click_spot, tuple):
                self.move_army_by_mouse_touch(click_spot)
                return
            elif isinstance(click_spot, str):
                self.menu_button_actions(click_spot)
                return
        x, y = self.active_spot
        delta = (0,0) # pass (dx, dy) into center_on()
        prv = False
        nxt = False
        if keys[pygame.K_7] or keys[pygame.K_KP7]:
            x -= 1
            if x % 2 == 0:
                y -= 1
                delta = (-1, -1)
            else:
                delta = (-1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_8]  or keys[pygame.K_KP8]:
            y -= 1
            delta = (0, -1)
        elif keys[pygame.K_9] or keys[pygame.K_KP9]:
            x += 1
            if x % 2 == 0:
                y -= 1
                delta = (1, -1)
            else:
                delta = (1, 0)
        elif keys[pygame.K_1] or keys[pygame.K_KP1]:
            x -= 1
            if x % 2 != 0:
                y += 1
                delta = (-1, 1)
            else:
                delta = (-1, 0)
        elif keys[pygame.K_DOWN] or keys[pygame.K_2] or keys[pygame.K_KP2]:
            y += 1
            delta = (0, 1)
        elif keys[pygame.K_3] or keys[pygame.K_KP3]:
            x += 1
            if x % 2 != 0:
                y += 1
                delta = (1, 1)
            else:
                delta = (1, 0)
        elif keys[pygame.K_LEFT] or keys[pygame.K_4] or keys[pygame.K_KP4]:
            prv = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_6] or keys[pygame.K_KP6]:
            nxt = True
        elif keys[pygame.K_v]:
            self.view_mode()
            return
        elif keys[pygame.K_r] and self.active_army.range_attack > 0:
            self.range_attack()
            self.next_army()
            self.shift_map_pane()
            self.cursor.update(self.active_spot, self.view_x_min, self.view_y_min)            
            return
        elif keys[pygame.K_b]: # barricade
            if self.active_army.type == 3 and self.active_army.barricade_points < 2:
                self.active_army.barricade_points += 1
            elif self.active_army.barricade_points > 0:
                self.menu_display(["Barricade defense",f"already max: {self.active_army.barricade_points + self.active_army.defense}"], ephemeral=True)
                return
            else:
                self.active_army.barricade_points += 1
            def_lvl = self.active_army.barricade_points + self.active_army.defense
            self.menu_display(f"Barricade: Defense now {def_lvl}","Wheat", wait=2)            
            self.next_army()
            self.shift_map_pane()
            return
            
        elif keys[pygame.K_SPACE] or keys[pygame.K_5] or keys[pygame.K_KP5]:
            if self.active_army.moves_left >= self.active_army.moves:
                self.active_army.mobilize_points += 1 # LATER: reset to zero if move
                self.menu_display(f"Mobility is now {self.active_army.moves + self.active_army.mobilize_points}")
            self.next_army()
            self.shift_map_pane()
            return True

        if not self.on_board((x,y)):
            # shift view to active unit
            if (x,y) in self.board:
                self.shift_map_pane()
            else:
                self.menu_display(f"Invalid move")
                print(f"DEBUG [not on board] active_spot {self.active_spot} ... {self.active_army.spot()}")
                return False

        # don't need movement points to attack
        if self.has_army((x,y)) and (x != self.active_spot[0] or y != self.active_spot[1]):
            this_army = [a for a in self.armies if a.spot() == (x,y)][0]
            if this_army.owner != 0:
                war_ratio = (self.active_army.attack*self.active_army.gen.war) / (1+ (this_army.attack*this_army.gen.war))
                advantage = self.active_army.gen.name if war_ratio > 1 else this_army.gen.name
                self.menu_display([f"{self.active_army.gen.name} attacking",
                                   f"{this_army.gen.name}",
                                   f"Might {self.active_army.attack} vs {this_army.defense}",
                                   f"Leaders {self.active_army.gen.war} vs {this_army.gen.war}",
                                   f"Advantage: {self.active_army.gen.name}",
                                   ], "red", replace=True)
                self.attack(this_army) # detached from self.armies?                
                self.next_army()
                self.shift_map_pane()
                return False

        # compare next terrain and remaining movement points        
        terrain_cost = self.move_cost[self.board[(x,y)].image_key]
        # adjust for +naval
        if self.board[(x,y)].image_key == 'w' and self.active_army.gen.specialty == 'naval':
            terrain_cost = 6            
        moves_left = self.active_army.moves_left
        if terrain_cost > moves_left:
            if self.board[(x,y)].image_key == "m":
                self.menu_display(f"Cannot cross mountains.", "Yellow", ephemeral=True)
            else:
                self.menu_display(f"That move costs ({terrain_cost} vs {moves_left})", "Yellow", ephemeral=True)
            return False

        # actually move piece
        if (self.on_board((x,y)) and
            self.has_army((x,y)) is False and
            (x != self.active_spot[0] or y != self.active_spot[1]) # x and/or y changed
            ):
            self.active_army.x = x
            self.active_army.y = y
            self.active_army.moves_left = moves_left - terrain_cost
            self.active_army.mobilize_points = 0 # reset after moving
            self.active_army.barricade_points = 0 # rest after moving
            # ^^ testing showed drawing here wasn't necessary; covered by self.draw_map()
            if not self.more_moves_possible():
                self.next_army()
            else:
                self.active_spot = (x,y)            
            self.shift_map_pane()         
            return True
        elif (x == self.active_spot[0] and y == self.active_spot[1]):
            return False # key pressed, but not a movement key
        elif self.has_army((x,y)) and (x != self.active_spot[0] or y != self.active_spot[1]):
            this_army = [a for a in self.armies if a.spot() == (x,y)][0]
            if this_army.owner == 0:
                self.menu_display(f"Invalid move", ephemeral=True)
                return False
        else:            
            return False
    def next_army(self):
        self.DEBUG_every_army_moved.append(f"{self.active_army.owner} {self.active_army.gen.name[:5]}")
        self.a += 1        
        if self.a > (len(self.armies)-1):
            if len(self.DEBUG_every_army_moved) < len(self.armies):
                print("DEBUG ERROR - not every army moved", self.DEBUG_every_army_moved)
            self.turn += 1
            self.menu_display(f'Next turn: {self.turn}', ephemeral=True, replace=True, wait=(0.5 *self.wait))
            self.a = 0            
            # check if battle time is up:
            if self.turn > self.last_turn:
                self.banner([f'Battle is over',f"{self.last_turn} days are up"])
                self.clock.tick(0.33 * self.wait)
                self.game_end = 'Time up'
                return
            # check if all castles occupied by invader
            if self.all_castles_occupied():
                self.banner(["Battle is over:", "Invading army", "controls castles"])
                self.clock.tick(0.33 * self.wait)
                self.game_end = 'Castles taken'
                return
            # reset movement points for each army; adjust for saved mobilize points
            for a in range(len(self.armies)):
                self.armies[a].moves_left = self.armies[a].moves + self.armies[a].mobilize_points
            self.active_army = self.armies[self.a]
            self.active_spot = self.active_army.spot()
            self.shift_map_pane()
            self.cursor.update(self.active_spot, self.view_x_min, self.view_y_min)
        self.active_army = self.armies[self.a]
        self.active_spot = self.active_army.spot()
        # check if either side is defeated; AI vs AI mode
        if hasattr(self, 'players') and isinstance(self.players, (tuple, list)):
            for player_num in self.players:
                player_remaining = any([army for army in self.armies if army.owner == player_num])
                if player_remaining is False:
                    self.banner([f'Battle is over',f"Player {player_num} defeated"])
                    self.clock.tick(0.33 * self.wait)
                    self.game_end = f"Player {player_num} lost"
                    return (f"Player {player_num} lost")
        else: # check if defeated, human vs AI mode
            player_remaining = any([army for army in self.armies if army.owner == 0])
            enemy_remaining = any([army for army in self.armies if army.owner != 0])
            if enemy_remaining is False:
                self.banner([f'Battle is over',"You are victorious!"])
                self.clock.tick(0.33 * self.wait)
                self.game_end = 'Defender lost'
                return ('Defender lost')
            if player_remaining is False:
                self.banner([f'Battle is over',"You lost"])
                self.clock.tick(0.33* self.wait)
                self.game_end = 'Invader lost'
                return ('Invader lost')
        
    def more_moves_possible(self):
        # checks for ANY possible movement to active_army's adjacent hexes
        (x,y) = self.active_army.spot()
        spot = self.active_spot
        moves_left = self.active_army.moves_left
        adjacent = [(x,y+1), (x+1,y), (x+1,y+1), (x-1,y), (x,y-1), (x-1,y-1)]
        for adj in adjacent:
            if self.board.get(adj) and self.move_cost[self.board[adj].image_key] <= moves_left:
                return True
        return False
    def adjacent_armies(self):
        # detects friend and foe adj armies separately
        locations = {'friend':[], 'foe':[]}
        for army in self.armies:
            if self.is_adjacent(army.spot()) and army.owner == self.active_army.owner:
                locations['friend'].append(army.spot())
            elif self.is_adjacent(army.spot()) and army.owner != self.active_army.owner:
                locations['foe'].append(army.spot())
        return locations
    
    def attack(self, enemy):
        def_bonus = self.terrain_defense[self.terrain_spot(enemy.spot())]
        # specialty adds +1 to attack, or if pikemen, +1 to defense, or if range, +1 range attack
        if self.active_army.gen.specialty == self.active_army.type and self.active_army.type in (0,1,2,5):
            spec_bonus = 1
        else:
            spec_bonus = 0
        if enemy.gen.specialty == enemy.type and enemy.type == 3:
            spec_def_bonus = 1 # pikemen get +1 def
        else:
            spec_def_bonus = 0
        army_ratio = (self.active_army.attack + spec_bonus) / (enemy.defense + enemy.barricade_points + spec_def_bonus)
        war_ratio = (self.active_army.gen.war/enemy.gen.war)
        old_war_ratio = war_ratio
        if war_ratio > 1:
            war_ratio = war_ratio/(math.sqrt(war_ratio)) # approx divides by max 3
        elif war_ratio <= 1:
            war_ratio = math.sqrt(war_ratio)
        player_attack = war_ratio * army_ratio
        #print(f'calc: {war_ratio} * {def_bonus} * {army_ratio}')        
        # IF SMALL ARMY, reduce total deaths        
        enemy_defense = 1/player_attack * def_bonus

        total_loss = 1000 if self.active_army.gen.war > 50 else (600 + (self.active_army.gen.war/100)*400)
        if enemy.size < 1000:
            total_loss = (0.25*total_loss + (total_loss * (enemy.size/1200)))
        if self.active_army.size < 1000:
            total_loss = (0.25*total_loss + (total_loss * (self.active_army.size/1200)))
        # calc fraction of 640-800 or 1000 troops lost to each side
        player_loss = enemy_defense / (player_attack + enemy_defense) * total_loss
        enemy_loss = player_attack / (player_attack + enemy_defense) * total_loss
        # animate attack
        text1 = self.font.render(self.active_army.shorthand(), True, Color("white"), Color("black"))
        text2 = self.font.render(self.active_army.shorthand(), True, Color("black"), Color("white"))
        etext1 = self.font.render(enemy.shorthand(), True, Color("white"), Color("black"))
        etext2 = self.font.render(enemy.shorthand(), True, Color("black"), Color("white"))
        text3 = self.font.render(self.active_army.shorthand(), True, Color("black"), Color("red"))
        etext3 = self.font.render(enemy.shorthand(), True, Color("black"), Color("red"))
        
        def animate(self, enemy, player0text, enemy1text):
            surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            surf.blit(self.active_army.shield, self.active_army.rect.topright)
            surf.blit(player0text, self.active_army.rect.midtop)
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(enemy1text, enemy.rect.midtop)
            self.clock.tick(16 * self.wait)
            pygame.display.flip()
        for frame in range(8):
            animate(self, enemy, text1, etext2)
            animate(self, enemy, text2, etext1)
            animate(self, enemy, text3, etext1)
            animate(self, enemy, text1, etext3)
        # if large enemies clash, or simultaneous attacks, subtract additional random armies - dice roll bonus
        if (self.active_army.size + enemy.size) > 15000:
            die_roll_loss = int(random.random()*300)
            player_loss += die_roll_loss
            enemy_loss += (300 - die_roll_loss)
        self.active_army.size = int(max(self.active_army.size - player_loss, 0))
        enemy.size = int(max(enemy.size - enemy_loss, 0))
        self.active_army.barricade_points = 0
        enemy.barricade_points = 0
        self.active_army.draw(self.view_x_min, self.view_y_min)
        enemy.draw(self.view_x_min, self.view_y_min)
        pygame.display.flip()
        self.clock.tick(2 * self.wait)
        # CAPTURED?
        if enemy.size == 0:
            self.menu_display([f"{enemy.gen.name}","has been captured!"], "Red", wait=(0.5 * self.wait))
            self.dead_armies.append(enemy)
            self.armies.remove(enemy)
            self.board[enemy.spot()].draw(self.view_x_min, self.view_y_min)
            self.clock.tick(0.5 * self.wait)
            pygame.display.flip()
        if self.active_army.size == 0:            
            self.menu_display([f"{self.active_army.gen.name}","has been captured!"], "Red", wait=(0.5 * self.wait))
            self.dead_armies.append(self.active_army)
            self.armies.remove(self.active_army)
            self.board[self.active_spot].draw(self.view_x_min, self.view_y_min)
            self.clock.tick(0.5 * self.wait)
            pygame.display.flip()        

    def draw_map(self):
        screen.fill(self.BACKGROUND)
        for piece in self.on_screen():
            #if self.turn == 1 and piece == self.active_spot:
            #    print(self.active_army.spot())
            #    # bug first turn / first army doesn't appear to move, only cursor moves.
            #    print(self.active_spot, self.active_army.gen.name, self.board[piece].image_key)
            (x,y) = piece
            cam_x = x - self.view_x_min
            cam_y = y - self.view_y_min
            surf.blit(self.board[piece].image, (self.edge + (cam_x*self.tile), self.offset(cam_x) + self.edge + (cam_y*self.tile)))
        [a.draw(self.view_x_min, self.view_y_min) for a in self.armies if a.spot() in self.on_screen()]
        self.menu_active_army_stats()
        pygame.display.flip()

    def shift_map_pane(self, spot=None):
        # to rationalize, save pane names with logical names like (0,0), (1,0) ... (2,2)
        # then set self.pane to these programmatically.
        (xmin, xmax, ymin, ymax) = self.map_panes[self.pane]
        if spot:
            (x,y) = spot
        else:
            (x,y) = self.active_spot
        (px,py) = self.pane
        prev_pane = self.pane
        margin = 2
        if x > (xmax - margin) and px < 3:
            px += 1
        if x < (xmin + margin) and px > 0:
            px -= 1
        if y > (ymax - margin) and py < 2:
            py += 1
        if y < (ymin + margin) and py > 0:
            py -= 1
        self.pane = (px, py)
        (xmin, xmax, ymin, ymax) = self.map_panes[self.pane]
        self.view_x_min = xmin
        self.view_x_max = xmax
        self.view_y_min = ymin
        self.view_y_max = ymax
        """
        if prev_pane != self.pane:
            # animate scrolling here
            # need to decide which direction to scroll;
            # and blit the next tiles as it scrolls
            #temp = pygame.transform.laplacian(surf) # finds edges --> new surf
            temp = surf.copy()
            chunk = (66*7)/ 10
            for i in range(10):
                surf.fill(self.BACKGROUND)
                surf.blit(temp, (0 - chunk*i,0), (0,0, temp.get_width() - chunk*i, temp.get_height()) )
                pygame.display.flip()
                clock.tick(30)
        """
        self.draw_map()
        
    def is_adjacent(self, other_spot, this_spot=None):
        # active_army or this_spot -- adjacent returns True/False; accounts for even-odd X-columns
        if not this_spot:
            (x,y) = self.active_army.spot()
        else:
            (x,y) = this_spot
        (x2, y2) = other_spot

        if (x-1) == x2 and (x % 2 != 0) and (y-1) == y2: # only ODD x-rows work
            return True # up and left
        elif (x-1) == x2 and (x % 2 == 0) and (y == y2):
            return True # up and left
        elif (x == x2) and (y-1) == y2:
            return True # up
        elif (x+1) == x2 and (x % 2 != 0) and (y-1) == y2: # up and right
            return True
        elif (x+1) == x2 and (x % 2 == 0) and (y == y2): # up and right
            return True
        elif (x-1) == x2 and (x % 2 == 0) and (y+1) == y2: # down and left
            return True
        elif (x-1) == x2 and (x % 2 != 0) and (y == y2): # down and left
            return True
        elif (x == x2) and (y+1 == y2):
            return True # down
        elif (x+1) == x2 and (x % 2 == 0) and (y+1) == y2: # down and right
            return True
        elif (x+1) == x2 and (x % 2 != 0) and (y == y2): # down and right
            return True
        return False # none of these are True
    
    def view_mode(self):
        """allows you to move a cursor around the board; runs inside BoardState."""
        # TESTING BALLISTA ranges
        """
        blank_image = extra_images['a']
        print('ballista at', self.active_spot)
        for incr, _spot in enumerate(ComputerAI.list_spots_three_away(self.active_spot)):
            this = self.board[_spot]
            shift_x = self.view_x_min
            shift_y = self.view_y_min
            this_x = self.edge + this.pixelx - (self.tile * shift_x)
            this_y = self.edge + this.pixely - (self.tile * shift_y)
            rect = pygame.Rect(this_x,
                                this_y,
                                this.image.get_width(),
                                this.image.get_height())
            self.surf.blit(blank_image, rect.topleft)
            text = self.font_sm.render(str(incr+1), True, Color("white"))
            self.surf.blit(text, (this_x, this_y))
        pygame.display.flip()
        """
        self.menu_display(f"Press ESC to exit view mode", "Yellow", replace=True)
        saved_active_spot = self.active_spot
        status = None
        while status != 'done':
            self.cursor.draw(surf) # makes it blink
            pygame.display.flip()
            self.clock.tick(60 * self.wait)
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    status = 'done'
                if event.type == pygame.KEYDOWN:
                    result = self.view_mode_movement(keys)
                    if result == False:
                        status = 'done'
        self.active_spot = saved_active_spot
        self.shift_map_pane()                    
            
    def view_mode_movement(self, keys):
        (x, y) = self.active_spot        
        delta = (0,0)
        prv = False
        nxt = False
        if keys[pygame.K_7] or keys[pygame.K_KP7]:
            x -= 1
            if x % 2 == 0:
                y -= 1
                delta = (-1, -1)
            else:
                delta = (-1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_8] or keys[pygame.K_KP8]:
            y -= 1
            delta = (0, -1)
        elif keys[pygame.K_9] or keys[pygame.K_KP9]:
            x += 1
            if x % 2 == 0:
                y -= 1
                delta = (1, -1)
            else:
                delta = (1, 0)
        elif keys[pygame.K_1] or keys[pygame.K_KP1]:
            x -= 1
            if x % 2 != 0:
                y += 1
                delta = (-1, 1)
            else:
                delta = (-1, 0)
        elif keys[pygame.K_DOWN] or keys[pygame.K_2] or keys[pygame.K_KP2]:
            y += 1
            delta = (0, 1)
        elif keys[pygame.K_3] or keys[pygame.K_KP3]:
            x += 1
            if x % 2 != 0:
                y += 1
                delta = (1, 1)
            else:
                delta = (1, 0)
        elif keys[pygame.K_LEFT] or keys[pygame.K_4] or keys[pygame.K_KP4]:
            prv = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_6] or keys[pygame.K_KP6]:
            nxt = True
        elif keys[pygame.K_SPACE] or keys[pygame.K_5] or keys[pygame.K_ESCAPE] or keys[pygame.K_KP5]:
            return False
        if not self.on_board((x,y)):
            return
        self.active_spot = (x,y)
        self.shift_map_pane()
        self.cursor.update(self.active_spot, self.view_x_min, self.view_y_min)
        for army in self.armies:
            if self.active_spot == army.spot():
                self.menu_active_army_stats(army)
    def range_attack(self):
        """ replace hexes two away - archer targeting aid """
        # 1. show places you can hit        
        (x,y) = self.active_army.spot()
        current_spot = 0
        targets = ComputerAI.list_spots_two_away((x,y))
        if self.active_army.type == 6: #'balistas'
            targets = targets + ComputerAI.list_spots_three_away((x,y))
        """
        targets = [
            (x, y-2), # up
            (x+1, y-(2 if x % 2 != 0 else 1)), # only when X odd
            (x+2, y-1), # right and up
            (x+2, y),
            (x+2, (y if x % 2 != 0 else y+1)), # when odd             
            (x+1, y+(2 if x % 2 == 0 else 1)), # only when X even
            (x, y+2), # down 
            (x+2, y+1), # right and down (only when odd)
            (x-2, y-1),            
            (x-1, y+(2 if x % 2 == 0 else 1)), # only when X even
            (x-2, y), # left
            (x-2, (y if x % 2 != 0 else y+1)), # when odd
            (x-2, y+1),
            (x-1, y-(2 if x % 2 != 0 else 1)), # only when X odd            
        ]
        """
        target_image = extra_images['t2']
        targeted_image = extra_images['t']
        for spot in targets:
            if not self.on_board(spot):
                continue
            this = self.board[spot]
            rect = pygame.Rect(
                self.edge + this.pixelx - (self.tile * self.view_x_min),
                self.edge + this.pixely - (self.tile * self.view_y_min),
                this.image.get_width(),
                this.image.get_height())
            surf.blit(target_image, rect.topleft)
        
        # highlight first enemy army
        for army in self.armies:
            if army.owner != self.active_army.owner and army.spot() in targets:
                this = self.board[army.spot()]
                rect = pygame.Rect(
                    self.edge + this.pixelx - (self.tile * self.view_x_min),
                    self.edge + this.pixely - (self.tile * self.view_y_min),
                    this.image.get_width(),
                    this.image.get_height())
                surf.blit(targeted_image, rect.topleft)
                break
        pygame.display.flip()
        any_targets = any([army for army in self.armies
                                if army.owner != self.active_army.owner
                                and army.spot() in targets])
        if not any_targets:
            self.menu_display("No enemies in range.","Yellow")
            self.clock.tick(1 * self.wait)
            return

        # FUTURE TODO: TAB to rotate through targets
        # only highlight spots where an enemy army is found; skip empty ones.
        def rotate_target(current_spot): ### TODO FIX - not working yet ###
            if current_spot +2 > len(spots):
                current_spot = 0
                print("TAB reset 0")
            else:
                current_spot += 1
            this = self.board[targets[current_spot]]
            shift_x = self.view_x_min
            shift_y = self.view_y_min
            rect = pygame.Rect(self.edge + this.pixelx - (self.tile * shift_x),
                                self.edge + this.pixely - (self.tile * shift_y),
                                this.image.get_width(),
                                this.image.get_height())
            surf.blit(targeted_image, rect.topleft)
            pygame.display.flip()
        #if multiple_targets:
        #    self.menu_display("Press [TAB] to switch target", "Yellow")
            """
            status = None
            while status != 'done':
                self.cursor.draw(surf) # makes it blink
                pygame.display.flip()
                self.clock.tick(60)
                for event in pygame.event.get():
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE] or keys[pygame.K_5] or keys[pygame.K_ESCAPE]:
                        status = 'done'
                    if keys[pygame.K_TAB]:
                        result, current_spot = rotate_target(current_spot)
                        if result == False:
                            status = 'done'
            """
        self.menu_display(f"Ranged attack on {army.gen.name}!", "Yellow")
        # RANGE ATTACK
        enemy = army
        def_bonus = self.terrain_defense[self.terrain_spot(enemy.spot())]
        # add FOREST RANGE DEFENSE BONUS
        if self.board[enemy.spot()].image_key == 'f':
            def_bonus = 1.25
        gen_spec_bonus = (1 if (self.active_army.gen.specialty in (4,6,7,8) and
                                self.active_army.gen.specialty == self.active_army.type) else 0)
        army_ratio = (self.active_army.range_attack + gen_spec_bonus) / (enemy.defense + enemy.barricade_points)
        war_ratio = (self.active_army.gen.war/enemy.gen.war)
        if war_ratio > 1:
            war_ratio = war_ratio/(math.sqrt(war_ratio)) # approx divides by max 3
        elif war_ratio <= 1:
            war_ratio = math.sqrt(war_ratio)
        player_attack = war_ratio * army_ratio
        enemy_defense = 1/player_attack * def_bonus
        total_loss = 400 if self.active_army.gen.war > 60 else (200 + (self.active_army.gen.war/100)*200)
        die_roll_loss = int(random.random()*200)
        total_loss += die_roll_loss
        enemy_loss = int(player_attack / (player_attack + enemy_defense) * total_loss)
        # animate attack
        self.shift_map_pane(enemy.spot())
        etext1 = self.font.render(enemy.shorthand(), True, Color("white"), Color("black"))
        etext2 = self.font.render(enemy.shorthand(), True, Color("black"), Color("white"))
        etext3 = self.font.render(enemy.shorthand(), True, Color("black"), Color("red"))        
        def animate(self, enemy, enemy1text):
            surf.blit(enemy.image, enemy.rect.midtop)        
            surf.blit(enemy.shield, enemy.rect.topright)
            surf.blit(enemy1text, enemy.rect.midtop)
            self.clock.tick(16 * self.wait)
            pygame.display.flip()
        for frame in range(8):
            animate(self, enemy, etext2)
            animate(self, enemy, etext1)
            animate(self, enemy, etext1)
            animate(self, enemy, etext3)
        # adjust army size
        self.menu_display(f"Struck down {int(enemy_loss)} troops","Red")
        enemy.size = int(max(enemy.size - enemy_loss, 0))
        enemy.draw(self.view_x_min, self.view_y_min)
        enemy.barricade_points = 0
        self.active_army.barricade_points = 0
        self.clock.tick(2 * self.wait)
        # CAPTURED?
        if enemy.size == 0:
            self.menu_display(f"{enemy.gen.name} has been captured!", "Red", wait=(0.5 * self.wait))
            self.dead_armies.append(enemy)
            self.armies.remove(enemy)
            self.board[enemy.spot()].draw(self.view_x_min, self.view_y_min)
            self.clock.tick(0.5 * self.wait)
        self.draw_map() # remove target spots
        pygame.display.flip()

    def all_castles_occupied(self):
        castle_spots = [spot for spot in self.board if self.board[spot].image_key == 'c']
        invading_armies = [army for army in self.armies if army.owner == 0]
        filled_castles = []
        for spot in castle_spots:
            for army in invading_armies:
                if army.spot() == spot:
                    filled_castles.append(spot)
        if set(castle_spots) == set(filled_castles):
            return True
        return False

def game_loop(bs):    
    bs.banner(["Begin battle", f"{bs.last_turn} days left"], "Wheat")
    bs.active_army = bs.armies[0]
    bs.active_spot = bs.active_army.spot()
    bs.shift_map_pane()
    bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)
    
    while True:
        bs.cursor.draw(surf) # makes it blink        
        pygame.display.flip()
        bs.clock.tick(60 * bs.wait)
        if bs.active_spot == (0,0): # this hack deals with first move bug
            bs.active_spot = bs.armies[-1].spot()            
            bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)
            bs.next_army()            
            bs.clock.tick(1 * bs.wait)
            bs.shift_map_pane()            
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if bs.active_army.owner == 0:
                if event.type == pygame.KEYDOWN:
                    successful = bs.move_army(keys)
                    bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)
                elif event.type == pygame.MOUSEBUTTONDOWN:                    
                    bs.move_army(keys, mouse_pos=event.pos)
                    bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                elif event.type == pygame.FINGERDOWN:
                    bs.move_army(keys, mouse_pos=event.pos)
                    bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)
                elif event.type == pygame.FINGERUP:
                    pass
                elif event.type == pygame.FINGERMOTION:
                    pass
            for idx,(button,action,menutext,hovering) in enumerate(bs.menu_buttons):
                if button.collidepoint(pygame.mouse.get_pos()) and not hovering:
                    bs.surf.blit(bs.font_sm.render(menutext, True, Color("green")), (button.x, button.y))                    
                    bs.menu_buttons[idx][-1] = True
                elif hovering and not button.collidepoint(pygame.mouse.get_pos()):
                    bs.surf.fill(bs.BACKGROUND, rect=button)
                    bs.surf.blit(bs.font_sm.render(menutext, True, Color("DarkSeaGreen")), (button.x, button.y))
                    bs.menu_buttons[idx][-1] = False
        if bs.active_army.owner != 0:
            bs.shift_map_pane()
            bs.clock.tick(2 * bs.wait)
            bs.AI_choose_action()
            #bs.AI_move()
            bs.next_army()
            bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)
            if bs.game_end:
                return bs            
            if bs.active_army.owner == 0:
                bs.shift_map_pane()
                bs.cursor.update(bs.active_spot, bs.view_x_min, bs.view_y_min)

    return bs # to battle_test_AI
                
if __name__ == "__main__":
    # for battle_test_AI.py, need to pass in armies and board state
    bs = BoardState() # makes board; adds default armies
    bs.players_AI_level = {0:0, 1:4, 2:1}
    bs.armies = create_armies(bs.board)    
    game_loop(bs)
    pygame.quit() # only quits if run outside of battle_test_AI or outside full game
    sys.exit()
