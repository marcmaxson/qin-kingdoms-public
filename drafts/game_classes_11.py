import pygame
from pygame import Color
import random
import time
from collections import deque # bfs algo
with open('warlords.txt','r') as f:
    NAMES = f.read().split('\n')

""" DEFENDER AI
- functions to sense board state
    - nearest enemy
    - distance (in turns) to spot
    - compare total army strengths
    - choose best army to attack (weakest)
        or only barricade, if all other armies are way stronger
- functions that represent complex moves
    - attack adjacent enemy (based on relative strengths)
    - move towards weakest enemy
    - move towards nearest enemy
    - barricade next to archer (if pikemen, militia, or weaker general, based on relative strengths)
    - return to castle
    - defend castle (barricade)
    - defend castle (attack)
    - move towards rice
    - mobilize (based on distance to rice)
    - feint (randomly move towards rice, then back to castle over 1 turns)
    - set up archers (with non archer unit in front
        with higher defense rating or cheaper unit cost to sacrifice)
"""

class ComputerAI():
    # assumes this is the defender side (owner=1)
    def __init__(self):
        self.AI_owner = 1 # enemy
        self.AI_role = 'defend' # vs 'attack'
        self.graph = self.convert_board_to_graph()
        
    def AI_choose_action(self):
        text1 = self.font.render(self.active_army.shorthand(), True, Color("white"), Color("black"))
        text2 = self.font.render(self.active_army.shorthand(), True, Color("black"), Color("white"))
        def animate(self, text):
            self.surf.blit(self.active_army.image, self.active_army.rect.midtop)        
            self.surf.blit(self.active_army.shield, self.active_army.rect.topright)
            self.surf.blit(text, self.active_army.rect.midtop)
            self.clock.tick(16)
            pygame.display.flip()            
        for frame in range(3):
            animate(self, text1)
            animate(self, text2)
        pass
    
    def AI_move(self):
        print(f"** {self.active_army.gen.name} {self.active_army.types[self.active_army.type]} {self.adjacent_armies()}")
        # point towards nearest enemy with less troops, and find fastest path there.
        #for army in self.armies:
        #    if self.is_adjacent(army.spot()):
        #        print(f"** DEBUG active_spot {self.active_spot} is adjacent to army at {army.spot()} **")

        path = self.enemy_army_path(self.active_army.spot(), 'nearest')
        weakest = self.find_weakest_enemy_army()
        self.AI_move_along_path(path)
        print(f"moved along path: {path} towards weakest {weakest['who']}")
        #print(weakest)
        #if weakest['spot'] == path[-1] and weakest['move'] == 'attack':
        #    print(f"closest is also weakest enemy: {weakest['who']}")
        #    self.AI_move_along_path(path)
        #    print('moved along path:', path)
        #elif weakest['ratio'] <= 3:
        #    # now move towards closest (if ratio < 3) or weakest otherwise
        #    path = self.enemy_army_path(self.active_army.spot(), weakest['spot'])
        #    self.AI_move_along_path(path)
        #    print('moved along path:', path)

        # mobilize (if there is a weakest enemy far away) or barricade (if not)
        # this also catches case where army must mobilize to cross a river
        if self.active_army.moves_left >= self.active_army.moves:
            if self.active_army.mobilize_points < 7:
                self.active_army.mobilize_points += 1 # LATER: reset to zero if move
                print(f"{self.active_army.gen.name}: Mobility is now {self.active_army.moves + self.active_army.mobilize_points}")
                self.menu_display(f"Mobility is now {self.active_army.moves + self.active_army.mobilize_points}")
            else:
                print(f"{self.active_army.gen.name}: Waiting; max mobility {self.active_army.moves + self.active_army.mobilize_points}")
                self.menu_display(f"Waiting; max mobility {self.active_army.moves + self.active_army.mobilize_points}")

        # always attack adjacent enemy, for now
        if self.more_moves_possible() and self.adjacent_armies()['foe']:
            for army in self.armies:
                if army.spot() in self.adjacent_armies()['foe']:
                    print(f"AI ATTACKING {self.active_army.gen.war} vs {army.gen.war}")
                    war_ratio = (self.active_army.attack*self.active_army.gen.war) / (1+ (army.attack*army.gen.war))
                    advantage = self.active_army.gen.name if war_ratio > 1 else army.gen.name
                    self.menu_display([f"{self.active_army.gen.name} attacking",
                                       f"{army.gen.name}",
                                       f"{self.active_army.attack} vs {army.defense}",
                                       f"{self.active_army.gen.war} vs {army.gen.war}",
                                       f"Advantage: {advantage}",
                                       ], "wheat", replace=True)                    
                    self.attack(army)
                    # arbitrary attacks first one detected.

    def AI_move_along_path(self, path):
        if len(path) == 0:
            print(f"ERROR no path to enemy")
            return
        # remove start/end spots; usually contain army
        if self.has_army(path[0]):
            path = path[1:]
        if self.has_army(path[-1]):
            path = path[:-1]

        broken = None
        for spot in path:
            # each call moves a single hex space
            (x,y) = self.active_army.spot()
            (x2, y2) = spot
            terrain_cost = self.move_cost[self.board[(x,y)].image_key]
            moves_left = self.active_army.moves_left        
            if self.has_army(spot):
                broken = f'army at {x,y} blocked at {spot}'
            elif (x == x2 and y == y2):
                broken = 'same spot'
            elif terrain_cost > moves_left:
                broken = 'no moves left'
            else:                
                self.active_army.x = x2
                self.active_army.y = y2
                self.active_army.moves_left = moves_left - terrain_cost
                self.active_army.mobilize_points = 0 # reset after moving army
                self.active_spot = spot

            # animate move
            self.shift_map_pane()
            self.draw_map()
            print(f"DEBUG {self.active_army.gen.name} moved {(x,y)} to {self.active_army.spot()}")
            self.clock.tick(2)
            if broken or not self.more_moves_possible():
                #self.next_army() -- managed in game loop
                break
            
        if broken:
            print(f"** AI move blocked [{broken}]")
        
    
    def convert_board_to_graph(self, exclude_spots=()):
        # only runs inside BoardState class
        # "self.graph is a lookup dict with keys: MapHex spots, values: list of adjacent spots."        
        graph = {}
        for (xx, yy) in self.board:
            neighbors = [(xx, yy+1), (xx, yy-1), (xx+1, yy), (xx-1, yy), (xx-1, yy-1), (xx-1, yy+1), (xx+1, yy-1), (xx+1, yy+1)]
            neighbors = [spot for spot in neighbors if (0 <= spot[0] <= (self.board_width-1)) and (0 <= spot[1] <= (self.board_height-1))]
            neighbors = [spot for spot in neighbors if self.is_adjacent(spot, (xx, yy))] # REALLY SURE spots are adjacent
            # remove mountains as neighbors; untraversible
            neighbors = [spot for spot in neighbors if self.board[spot].image_key != 'm']
            neighbors = [spot for spot in neighbors if spot not in exclude_spots]
            graph[(xx, yy)] = neighbors
        return graph

    def enemy_army_spots(self):
        return [army.spot() for army in self.armies if army.owner == 0]
            
    def enemy_army_path(self, spot, how='nearest'):
        # does NOT move around occupied spots in the path
        # paths start and end with army; don't count these
        #if any([self.has_army(spot) for spot in path[1:-1]]):
        #    print(f"DEBUG occupied: {[self.has_army(spot) for spot in path]}")
        #        continue
        # BAD FIX: re-calc graph each time, excluding occupied spots (but including this army and target army)
        #GOOD FIX: when actually moving, if next move is occupied, then move adjacent to it and recalculate path.

        paths = []
        if how == 'nearest':
            for enemy_spot in self.enemy_army_spots():
                paths.append(self.bfs_shortest_path(spot, enemy_spot))
        elif isinstance(how,tuple):
            enemy_spot = how
            paths.append(self.bfs_shortest_path(spot, enemy_spot))
        # adjust weights of paths by movement costs        
        weighted_paths = []
        for path in paths: 
            total_move_cost = 0
            for spot in path[1:-1]:
                total_move_cost += self.move_cost[self.board[spot].image_key]
            weighted_paths.append([total_move_cost, path])
        shortest = sorted(weighted_paths, key=lambda x:x[0])[0][1] # small-to-big
        return shortest #print(f"DEBUG nearest enemy path {shortest}")
        return paths[0]
    
    def bfs_shortest_path(self, f_spot, to_spot):
        """ https://medium.com/@yasufumy/algorithm-breadth-first-search-408297a075c9 """

        def backtrace(parent, start, end):
            path = [end]
            while path[-1] != start:
                path.append(parent[path[-1]])
            path.reverse()
            return path
        
        queue = deque([f_spot])
        # The level holds distances from the vertex from which we start searching.
        level = {f_spot: 0}
        # The parent holds the vertex just added as a key and the vertex
        # from which we reach to the vertex just added as a value.
        parent = {f_spot: None}
        # "self.graph is a lookup dict with keys: MapHex spots, values: list of adjacent spots."
        # each time, exclude other armies on the same side (excluding enemies would make path un-calculable)
        graph = self.convert_board_to_graph((army.spot() for army in self.armies if army.owner == self.active_army.owner))
        while queue:
            spot = queue.popleft()
            for n in graph[spot]:
                if n not in level:
                    queue.append(n)
                    level[n] = level[spot] + 1
                    parent[n] = spot
                # increment the i after the for-loop finishes to expand the circle to search.
        # typical output:
        # ({'A': 0, 'B': 1, 'C', 1, 'D': 2, 'E', 2},
        # ints: level -- how many hops from current spot to any other spot on map.
        # {'A': None, 'B': 'A', 'C': 'A', 'D', 'B', 'E', 'B'})  # parent -- every spot's
        # we can know the path(which spots to hop in sequence) by back-tracing the parent
        try:
            path = backtrace(parent, f_spot, to_spot)
        except:
            print("error backtrace")
            return []
        return path

    def find_weakest_enemy_army(self):
        # also specifies whether to attack them to defend against them or use ranged attack.
        # track each using army.gen.name
        own_attack = self.active_army.size * self.active_army.attack * self.active_army.gen.war
        own_defense = self.active_army.size * self.active_army.defense * self.active_army.gen.war
        own_range = self.active_army.size * self.active_army.range_attack * self.active_army.gen.war
        #print(self.active_army.gen.name, self.active_army.gen.war, self.active_army.attack, self.active_army.defense, self.active_army.size)
        enemies = []
        for army in self.armies:
            if army.owner != self.AI_owner:
                enemy_att = army.size * army.attack * army.gen.war
                enemy_def = army.size * army.defense * army.gen.war
                enemy_range = army.size * army.range_attack * army.gen.war
                enemies.append([army.gen.name, 'defend against', enemy_att, round(own_defense/enemy_att,2), army.spot()])
                enemies.append([army.gen.name, 'attack', enemy_def, round(own_attack/enemy_def,2), army.spot()])
                if own_range != 0 and enemy_range == 0:
                    enemies.append([army.gen.name, 'ranged attack', enemy_def, round(own_range/enemy_def,2), army.spot()])
                if enemy_range != 0 and own_range == 0:
                    enemies.append([army.gen.name, 'ranged defense', enemy_range, round(own_defense/enemy_range,2), army.spot()])
                if enemy_range != 0 and own_range != 0:
                    enemies.append([army.gen.name, 'mutual range', enemy_range, round(own_range/enemy_range,2), army.spot()])
        best_enemy = sorted(enemies, key=lambda x:x[3], reverse=True)[0]
        #print(best_enemy)
        if best_enemy[3] > 1:
            return {'who': best_enemy[0], 'move':'attack', 'ratio':best_enemy[3], 'meta':best_enemy[1], 'spot':best_enemy[4]}
        else:
            return {'who': best_enemy[0], 'move':'barricade', 'ratio':best_enemy[3], 'meta':best_enemy[1], 'spot':best_enemy[4]}


def random_shield():
    raw = SpriteSheet("sheet-crests-28.jpg")
    rects = []
    for x in range(8):
        for y in range(8):
            rects.append((28*x, 28*y, 28, 28))
    images = raw.images_at(rects)
    return random.choice(images)     


def offset(x, tile=66):
    if x % 2 == 0:
        y_offset = int(0.5 * tile)
    else:
        y_offset = 0
    return y_offset


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
    def update(self, active_spot, shift_x=0, shift_y=0):
        (x,y) = active_spot
        self.rect = pygame.Rect(
            self.edge + (x - shift_x)*self.tile,
            self.edge + (y - shift_y)*self.tile + offset(x),
            self.tile, self.tile)
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
        self.exp = 0 # more experience results in more soldiers captured/wounded-added to army size after
    

class SideMenu():
    X_menu_top = 20
    X_menu_left = 520
    X_menu_row = 30

    def __init__(self):
        pass # these settings don't seem to get created with super()
        #self.X_menu_top = 0
        #self.X_menu_left = 560 # 240-width available
        # BoardState includes self.font, self.surf, self.clock
        # colors: Green, DarkSeaGreen (plains yellow), DarkOliveGreen (forest)

    def menu_active_army_stats(self):
        moves = self.active_army.moves_left + self.active_army.mobilize_points
        moves_color = "Red" if self.active_army.mobilize_points > 0 else "DarkSeaGreen"
            
        special = self.active_army.gen.specialty
        attack = f"({self.active_army.attack}/{self.active_army.defense})"
        if self.active_army.range_attack > 0:
            attack = f"R{self.active_army.range_attack} ({self.active_army.attack}/{self.active_army.defense})"            
        if isinstance(special, int):
            special = self.active_army.types[self.active_army.gen.specialty]
        items = [
            (f"{self.active_army.gen.name}",'Green'),
            (f"War: {self.active_army.gen.war} Int: {self.active_army.gen.int} Cha: {self.active_army.gen.cha}","DarkOliveGreen"),
            (f"Specialty: {special.title()}","DarkOliveGreen"),
            (f"{self.active_army.types[self.active_army.type].title()} {attack}","DarkSeaGreen"),
            (f"Moves: {moves}",moves_color),
            (f"Troops: {self.active_army.size}","DarkSeaGreen"),
        ]
        self.menu_last_row = 0
        for row in items:
            x = SideMenu.X_menu_left
            y = SideMenu.X_menu_top + (self.menu_last_row * SideMenu.X_menu_row)
            text = self.font_sm.render(row[0], True, Color(row[1]))
            self.menu_last_row += 1
            self.surf.blit(text, (x, y))            
        pygame.display.flip()
     
    def menu_display(self, message, color="Wheat", wait=True, ephemeral=False, replace=False): # or "PaleGoldenRod"
        """ ephemeral: waits, and then erases it and moves last row backwards."""
        if not isinstance(message, (tuple, list)):
            message = [message]
        if replace:
            self.surf.fill(self.BACKGROUND, (SideMenu.X_menu_left, SideMenu.X_menu_top, 280, self.menu_last_row * SideMenu.X_menu_row))
            self.menu_last_row = 0
        for row in message:
            x = SideMenu.X_menu_left
            y = SideMenu.X_menu_top + (self.menu_last_row * SideMenu.X_menu_row)
            text = self.font_sm.render(row, True, Color(color))
            self.menu_last_row += 1
            self.surf.blit(text, (x, y))            
        pygame.display.flip()
        if wait == True:
            self.clock.tick(2)
        elif isinstance(wait, (int,float)):
            self.clock.tick(wait)            
        if ephemeral:
            self.menu_last_row -= len(message)
            for row in message:                
                x = SideMenu.X_menu_left
                y = SideMenu.X_menu_top + (self.menu_last_row * SideMenu.X_menu_row)
                #text = self.font_sm.render(40*" ", False, Color(color))
                self.surf.fill(self.BACKGROUND, (x, y, 280, SideMenu.X_menu_row))
                self.menu_last_row += 1
                #self.surf.blit(text, (x, y))
            pygame.display.flip()
            self.menu_last_row -= len(message)
            
            
            