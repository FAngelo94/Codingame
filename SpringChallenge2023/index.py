import sys
import math



number_of_cells = int(input())  # amount of hexagonal cells in this map
number_of_bases = 0  # amount of bases
my_bases = []  # list of my bases
opp_bases = []  # list of opponent bases
cells = []  # list of cells
turn = 1
total_my_ants = 0
total_opp_ants = 0
total_christals = 0
remain_christals = 0
total_eggs = 0
remain_eggs = 0
my_score = 0
opp_score = 0

FORCE_STRATEGY_2 = 10

for i in range(number_of_cells):
    # _type: 0 for empty, 1 for eggs, 2 for crystal
    # initial_resources: the initial amount of eggs/crystals on this cell
    # neigh_0: the index of the neighbouring cell for each direction
    _type, initial_resources, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    cells.append({
        'type': _type,
        'initial_resources': initial_resources,
        'neighs': [neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5],
        'my_ants': 0,
        'opp_ants': 0,
    })
    if _type == 1:
        total_eggs += initial_resources
    elif _type == 2:
        total_christals += initial_resources

number_of_bases = int(input())
for i in input().split():
    my_base_index = int(i)
    my_bases.append(my_base_index)
for i in input().split():
    opp_base_index = int(i)
    opp_bases.append(opp_base_index)

def insert_in_order(commands, new_command):
    # oder by strength, first weakest
    if len(commands) == 0:
        commands.append(new_command)
        return commands
    for i in range(len(commands)):
        if new_command['strength'] < commands[i]['strength']:
            commands.insert(i, new_command)
            return commands
    commands.append(new_command)
    return commands

def print_commands_in_one_row(commands):
    row = []
    for c in commands:
        if c['type'] == 'LINE':
            row.append('LINE {} {} {}'.format(c['source'], c['target'], c['strength']))
        elif c['type'] == 'BEACON' and c['strength'] > 0:
            row.append('BEACON {} {}'.format(c['target'], c['strength']))
    print(';'.join(row))


def translate_roads_to_commands(roads, cells_under_attack):
    commands = []
    for cell in cells_under_attack:
        target = roads[cell][-1]
        # print("roads", roads[cell], file=sys.stderr, flush=True)
        for r in roads[cell]:
            strength = cells[target]['resources']
            commands = insert_in_order(commands, {
                'type': 'BEACON',	
                'target': r,
                'strength': 1,
            })
    return commands

def check_if_near_cells_under_attack(cell, distanceFromBase, cells_under_attack):
    roads= [[] for i in range(number_of_cells)]
    visited = []
    # add cell neighs to next_cells if not visited
    next_cells = [n for n in cells[cell]['neighs'] if n != -1]
    distance = 0
    while len(next_cells) > 0 and distance < distanceFromBase:
        distance += 1
        current_cells = next_cells
        next_cells = []
        for i in current_cells:
            visited.append(i)
            # add neighs to next_cells if not visited
            for j in cells[i]['neighs']:
                if j not in visited and j != -1 and j not in current_cells and j not in next_cells:
                    next_cells.append(j)
                    roads[j] = roads[i].copy()
                    roads[j].append(i)
            # check cell
            if cells[i]['type'] == 2 and cells[i]['resources'] > 0 and i in cells_under_attack:
                roads[i].append(i)
                return roads[i]
            elif cells[i]['type'] == 1 and cells[i]['resources'] > 0 and i in cells_under_attack:
                roads[i].append(i)
                return roads[i]
    return None

def strategy3():
    # if a cell contians crystal or eggs, send ants to it
    road_for_cells =  [[[b] for i in range(number_of_cells)] for b in my_bases]
    r = 0
    visited = my_bases.copy()
    egg_taking = 0 # egg in the cell under attack
    cells_under_attack = [] #my_bases.copy()
    commands = [] 
    available_ants = total_my_ants
    distance = 0
    next_cells = [[n for n in cells[my_bases[r]]['neighs'] if n != -1] for r in range(len(my_bases))]
    goOn = True
    christals_under_attack = 0
    eggs_under_attack = 0
    while distance < available_ants and goOn:
        r = 0
        distance += 1
        while r < len(my_bases):
            # print("next_cells", next_cells, file=sys.stderr, flush=True)
            # print("available_ants", available_ants, file=sys.stderr, flush=True)
            # print("distance", distance, file=sys.stderr, flush=True)
            not_enough_eggs =  total_my_ants < remain_christals / 2
            current_cells = next_cells[r]
            next_cells[r] = []
            for i in current_cells:
                if distance > available_ants:
                    break
                visited.append(i)
                # add neighs to next_cells if not visited
                for j in cells[i]['neighs']:
                    if j not in visited and j != -1 and j not in current_cells and j not in next_cells[r]:
                        next_cells[r].append(j)
                        road_for_cells[r][j] = road_for_cells[r][i].copy()
                        road_for_cells[r][j].append(i)  
                # check cell
                if cells[i]['type'] == 2 and cells[i]['resources'] > 0 and i not in cells_under_attack and christals_under_attack < remain_christals / 2:
                    check_better_road = check_if_near_cells_under_attack(i, distance, cells_under_attack)
                    if check_better_road != None:
                        road_for_cells[r][i] = check_better_road
                        available_ants -= len(check_better_road)
                    else:
                        available_ants -= distance
                    cells_under_attack.insert(0, i)
                    road_for_cells[r][i].append(i)
                    christals_under_attack += cells[i]['resources']
                elif cells[i]['type'] == 1 and cells[i]['resources'] > 0 and i not in cells_under_attack and not_enough_eggs and eggs_under_attack < remain_eggs / 2:
                    check_better_road = check_if_near_cells_under_attack(i, distance, cells_under_attack)
                    if check_better_road != None:
                        road_for_cells[r][i] = check_better_road
                        available_ants -= len(check_better_road)
                    else:
                        available_ants -= distance
                    cells_under_attack.insert(0, i)
                    road_for_cells[r][i].append(i)
                    egg_taking += cells[i]['resources']
                    eggs_under_attack += cells[i]['resources']
            # print("available_ants in end", available_ants, file=sys.stderr, flush=True)
            commands += translate_roads_to_commands(road_for_cells[r], cells_under_attack)
            r += 1
        # check if next_cells is empty
        goOn = False
        for i in next_cells:
            if len(i) > 0:
                goOn = True
                break
    return commands

# game loop
while True:
    total_my_ants = 0
    total_opp_ants = 0
    turn += 1
    remain_christals = 0
    remain_eggs = 0
    my_score, opp_score = [int(i) for i in input().split()]
    for i in range(number_of_cells):
        # resources: the current amount of eggs/crystals on this cell
        # my_ants: the amount of your ants on this cell
        # opp_ants: the amount of opponent ants on this cell
        resources, my_ants, opp_ants = [int(j) for j in input().split()]
        cells[i]['resources'] = resources
        cells[i]['my_ants'] = my_ants
        cells[i]['opp_ants'] = opp_ants
        total_my_ants += my_ants
        total_opp_ants += opp_ants
        if cells[i]['type'] == 2:
            remain_christals += resources
        elif cells[i]['type'] == 1:
            remain_eggs += resources
    commands = strategy3()
    print_commands_in_one_row(commands)
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # WAIT | LINE <sourceIdx> <targetIdx> <strength> | BEACON <cellIdx> <strength> | MESSAGE <text>
    #print("WAIT")
