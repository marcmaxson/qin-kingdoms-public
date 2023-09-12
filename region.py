# main game file
# create a region full of 24 kingdoms
# create warlords (players) and populate kingdoms
# game loop for non-combat turns and seasons
import pygame
import numpy as np
#from sklearn.neighbors import KDTree
import random
from scipy.spatial import Voronoi


def generate_voronoi(width, height):
    """
    Randomly chooses various points within the [width] and [height] dimensions of the map.
    Then, uses SciPy to generate a voronoi diagram with them, and returns it.

    :return: SciPy voronoi diagram
    """
    point_arr = np.zeros([height, 2], numpy.uint16)
    for i in range(height):
        point_arr[i][0] = np.uint16(random.randint(0, width))
        point_arr[i][1] = np.uint16(random.randint(0, height))
    return Voronoi(point_arr)


def draw_voronoi(pygame_surface):
    # generate voronoi diagram
    vor = generate_voronoi()
    # draw all the edges
    for index_pair in vor.ridge_vertices:
        if -1 not in index_pair:
            start_pos = vor.vertices[index_pair[0]]
            end_pos = vor.vertices[index_pair[1]]
            pygame.draw.line(pygame_surface, (0, 0, 0), start_pos, end_pos)

class Region():

    def __init__(self):
        self.region_width = 100
        self.region_height = 100

    def connect(self):
        x = int(round(random.random()*self.region_width))
        y = int(round(random.random()*self.region_height))        
        coords = np.array([(i['x'],i['y']) for i in self.system_coords])
        nearest_tree = KDTree(coords)
        

class temp():

    def connect_galaxy(self):
        """ adds self.warps and self.wormholes to galaxy.
        then assigns system-positions of warp tiles within each system."""
        self.warps = {} # link lookup for every system to every other system (galaxy(x,y), galaxy(x2,y2)) keys.
        self.linked_systems = {} # lookup system A by 'id', get list of 'id' for connected systems.
        # also add this to system_coords list of dict
        self.wormholes = {} # these remain hidden and can only be accessed with dark matter tech
        self.system_warps = {} # saves warp-tile (x,y) locations in nested dict format: {from_system: {to_system_id:(x,y)}}
        from sklearn.neighbors import KDTree
        coords = np.array([(i['x'],i['y']) for i in self.system_coords])
        nearest_tree = KDTree(coords)
        #self.system_coords # id, name x, y
        # adding: warps, a list connected systems
        for idx,system in enumerate(self.system_coords):
            # pick a random number from 1 to N
            n_warps = int(round(random.triangular(1,MAX_WARPS)))
            # decide what the nearest system is
            this = np.array((system['x'], system['y'])).reshape(1, -1)
            dist, indeces = nearest_tree.query(this, k=(n_warps+1))
            xys = indeces.tolist()[0]
            # k neighbors will include "this" as first result; exclude zeroeth term.
            warp_coords = [(self.system_coords[i]['x'], self.system_coords[i]['y']) for i in xys[1:]]
            this_coord = tuple(this.tolist()[0])
            self.warps.update({(i,this_coord):1 for i in warp_coords}) # systems are stored as (x,y) coords on galaxy map, not system_id
            self.warps.update({(this_coord,i):1 for i in warp_coords}) # saves to both systems
            self.system_coords[idx]['warps'] = warp_coords # (x,y) for galaxy map.
            self.add_warps_to_this_system(system, this_coord, warp_coords)

        # now make a simpler lookup using system_ids from the [warps] data.
        for idx,system in enumerate(self.system_coords):
            self.linked_systems[system['id']] = []
            this_coord = (system['x'], system['y']) # (galaxy xy)
            # find all systems that are linked, using warp xy matches.
            for other_system in self.system_coords:
                for warp_xy in other_system['warps']:
                    if warp_xy == this_coord: # warps FROM other_system
                        if self.debug: print('pairing', system['id'], other_system['id'])
                        self.linked_systems[system['id']].append( other_system['id'] )

        for wormhole in range(int(random.triangular(3,9))):
            random_start = random.choice(coords)
            random_start = random_start.reshape(1, -1)
            startpoint = tuple(random_start.tolist()[0])
            dist, indeces = nearest_tree.query(random_start, k=len(coords))
            end_index = indeces.tolist()[0]
            # pick one of the farthest points
            end_index = random.choice(end_index[-5:])
            endpoint = (self.system_coords[end_index]['x'], self.system_coords[end_index]['y'])
            self.warps[(startpoint,endpoint)] = 1
            self.warps[(endpoint,startpoint)] = 1
            self.wormholes[(startpoint, endpoint)] = {'dark_matter':1}
            self.wormholes[(endpoint, startpoint)] = {'dark_matter':1}

        self.ensure_all_systems_connected()

    def add_warps_to_this_system(self, system, this_coord, warp_coords):
        """
        # add warp to edge of system; need only be unique vs other warps in system.
        # how to know which side of system to place the warp?
        """
        if not self.system_warps.get(system['id']):
            #print('bug add_warps:', system['id'] ) -- each new system added this way
            self.system_warps[system['id']] = {}
        for other_coord in warp_coords:
            other_system_id = min([i['id'] for i in self.system_coords if i['x'] == other_coord[0] and i['y'] == other_coord[1]])
            vert_dist = abs(this_coord[1] - other_coord[1])
            horiz_dist = abs(this_coord[0] - other_coord[0])
            side = 'V' if vert_dist > horiz_dist else 'H'
            if side == 'V' and this_coord[1] < other_coord[1]: # south
                in_system_warp_xy = (random.choice(range(1,11)), 12)
            elif side == 'V' and this_coord[1] > other_coord[1]: # north
                in_system_warp_xy = (random.choice(range(1,11)), 0)
            elif side == 'H' and this_coord[0] > other_coord[0]: # east
                in_system_warp_xy = (0, random.choice(range(1,11)))
            elif side == 'H' and this_coord[0] < other_coord[0]: # west
                in_system_warp_xy = (12, random.choice(range(1,11)))
            #### DEBUG -- check for dupes -- next ####################################
            #
            #
            self.system_warps[system['id']][other_system_id] = in_system_warp_xy
            #print(system['id'], other_system_id, in_system_warp_xy)
            # to be safe, add this to the other system too now; reverse X coords or Y coords, based on side
            if not self.system_warps.get(other_system_id):
                self.system_warps[other_system_id] = {}
            if side == 'V':
                in_system_warp_xy = (in_system_warp_xy[0], 12) if in_system_warp_xy[1] == 0 else (in_system_warp_xy[0],0)
                self.system_warps[other_system_id][system['id']] = in_system_warp_xy
            if side == 'H':
                in_system_warp_xy = (12,in_system_warp_xy[1]) if in_system_warp_xy[0] == 0 else (0,in_system_warp_xy[1])
                self.system_warps[other_system_id][system['id']] = in_system_warp_xy

    def ensure_all_systems_connected(self):
        #for thing in [self.linked_systems, self.system_warps]:
        systems = list(range(0,self.systems))
        results = Counter()
        warps = Counter()

        for system_A in systems:
            linksA = self.linked_systems.get(system_A)
            # warpsA is a dict of systemB ids --> sys(x,y) of warp
            warpsA = self.system_warps.get(system_A)
            if linksA in (None,[]):
                # find all systems paired to system_A, but not both-ways
                paired_systems = [B for (B, paired_list) in self.linked_systems.items() if system_A in paired_list]
                for B in paired_systems:
                    if self.linked_systems[system_A] is None:
                        self.linked_systems[system_A] = [B]
                    else:
                        self.linked_systems[system_A].append( B )
                if self.debug: print(f"fixed error testing linked_systems: {system_A} --> {self.linked_systems.get(system_A)}")
            if warpsA in (None,[]):
                print('error testing system_warps:', system_A) # this error has never come up
            results.update(linksA)
            for systemB, warp_xy in warpsA.items():
                warps[systemB] += 1
        if self.debug:
            print("connected systems")
            print(results.most_common())
            print("connected warps")
            print(warps.most_common())
    

from pygame import Color
DEBUG = False
HEIGHT = 600
WIDTH = 800
pygame.init()
game_surface = pygame.display.set_mode((WIDTH, HEIGHT))

draw_voronoi(game_surface)
