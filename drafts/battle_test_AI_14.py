from kingdoms import *
import json

def computer_armies(board, balanced_sides=True):
    """ player = invader = owner 2 vs defender, owner 1"""
    armies = [] # list of Army objects with Generals
    army_spots = [(2,2), (0,1), (5,3), (3,4)] 
    enemy_spots = [(8,8), (9,9), (10,9), (8,9)]
    player_shield = random_shield()
    enemy_shield = random_shield()
    if player_shield == enemy_shield:
        enemy_shield = random_shield()
    occupied_spots = []
    for idx, spot in  enumerate(army_spots):
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
                    type=random.randrange(0,7), owner=2,
                    size=random.choice([1333, 2666, 2400, 3100, 5500, 7850, 10100]),
                    shield=player_shield)
        armies.append( army )
    castle_spots = [spot for spot in board if board[spot].image_key == 'c']
    occupied_castles = []
    for idx, spot in enumerate(enemy_spots):
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
        if balanced_sides and (idx+1) == len(enemy_spots):
            invader_troops = sum([a.size for a in armies if a.owner != 1])
            defense_troops = sum([a.size for a in armies if a.owner == 1])
            if invader_troops > defense_troops:
                troops = invader_troops - defense_troops
            else:
                troops = random.choice([1333, 2666, 2400, 3100, 5500, 7850, 10100])
        else:
            troops = random.choice([4900, 2300, 3333, 5800, 1250, 900, 10100])
        # TODO: check that enemy armies don't occupy same spots
        army = Army(spot[0], spot[1],
                    type=random.randrange(0,7), owner=1,
                    size=troops,
                    shield=enemy_shield)
        armies.append( army )

    # balance invader if defense bigger
    if balanced_sides:
        invader_troops = sum([a.size for a in armies if a.owner != 1])
        defense_troops = sum([a.size for a in armies if a.owner == 1])
        if defense_troops > invader_troops:            
            for idx, army in enumerate(armies):
                if army.owner == 1:
                    if army.size > (defense_troops - invader_troops):
                        army.size = (defense_troops - invader_troops)
                        break
        invader_troops = sum([a.size for a in armies if a.owner != 1])
        defense_troops = sum([a.size for a in armies if a.owner == 1])
        print(f"balanced starting sides: invader {invader_troops} vs defender {defense_troops}")
    return armies

def log_game_status(bs, game_stats={}):
    invader = {'armies':[], 'total':0}
    defender = {'armies':[], 'total':0}
    for a in bs.armies:
        if a.owner == 2:
            invader['armies'].append({
                'size': a.size,
                'war': a.gen.war,
                'type': a.type,
                'spec': a.gen.specialty,
            })
            invader['total'] += a.size
        if a.owner == 1:
            defender['armies'].append({
                'size': a.size,
                'war': a.gen.war,
                'type': a.type,
                'spec': a.gen.specialty,
            })
            defender['total'] += a.size
    if game_stats == {}:
        game_stats = {
            "invader_start": invader,
            "defender_start": defender,
        }
    else:
        game_stats["invader_end"] = invader
        game_stats["defender_end"] = defender
    return game_stats

def battle_tracker(data, filename="battles.json"):
    """ logs each start and finish dataset dict to a JSON"""
    with open(filename,'r') as f:
        game_log = json.load(f)
    next_game_id = max([int(i) for i in list(game_log.keys())]) + 1
    print(next_game_id)
    game_log[next_game_id] = data
    with open(filename,'w') as f:
        json.dump(game_log, f, indent=2)
    print(f'logged game #{next_game_id}')
    return

def log_game_end(game_stats, bs, error=None):
    if hasattr(bs, 'battle_result'):
        game_stats["result"] = bs.battle_result
    if error:
        import traceback
        print("ERROR",error)
        traceback.format_exc()
        game_stats["error"] = str(error)
        battle_tracker(game_stats)
        return
    game_stats = log_game_status(bs, game_stats)
    battle_tracker(game_stats)

for _game in range(3):
    print(f"GAME {_game}")
    bs = BoardState() # makes board; adds default armies
    bs.armies = computer_armies(bs.board) # override default armies
    bs.players = [1,2]
    bs.wait = 50
    game_stats = log_game_status(bs)
    try:
        bs = game_loop(bs)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        log_game_end(game_stats, bs, error=e)
    log_game_end(game_stats, bs)
