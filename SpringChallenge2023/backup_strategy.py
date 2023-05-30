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

def calculate_distance(source, target):
    visited = []
    next_cells = [source]
    distance = -1
    while True:
        distance += 1
        current_cells = next_cells
        next_cells = []
        for i in current_cells:
            if i == target:
                return distance
            for j in cells[i]['neighs']:
                if j not in visited and j != -1 and j not in current_cells:
                    next_cells.append(j)
            visited.append(i)

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
        elif c['type'] == 'BEACON':
            row.append('BEACON {} {}'.format(c['target'], c['strength']))
    print(';'.join(row))

def nearest_cells_connected_to_base(cells_under_attack, new_cell):
    # starting from new_cell, find nearest cells connected to base
    visited = []
    next_cells = [new_cell]
    while True:
        current_cells = next_cells
        next_cells = []
        for i in current_cells:
            if i in cells_under_attack:
                return i
            for j in cells[i]['neighs']:
                if j not in visited and j != -1 and j not in current_cells:
                    next_cells.append(j)
            visited.append(i)

def strategy1():
    # if a cell contians crystal or eggs, send ants to it
    commands = []
    for i in range(number_of_cells):
        if (cells[i]['type'] == 2 or cells[i]['type'] == 1) and cells[i]['resources'] > 0:
            for b in my_bases:
                commands = insert_in_order(commands, {
                    'type': 'LINE',	
                    'source': b,
                    'target': i,
                    'strength': 1
                })
    # print commands seperated by ;
    return commands

def strategy1plus():
    # if a cell contians crystal or eggs, send ants to it
    road_for_cells = [[] for i in range(number_of_cells)]
    commands = []
    available_ants = total_my_ants - len(my_bases)
    visited = []
    next_cells = my_bases
    egg_taking = 0 # egg in the cell under attack
    cells_under_attack = my_bases.copy()
    roads = [[[] for i in range(number_of_cells)] for j in range(number_of_bases)]
    while available_ants > 0 and goOn and len(next_cells) > 0:
        current_cells = next_cells
        next_cells = []
        for i in current_cells:
            visited.append(i)
            distance = calculate_distance(i, my_bases[0])
            not_enough_eggs = egg_taking + total_my_ants < remain_christals / 2
            too_far = cells[i]['resources'] < distance
            few_resources = cells[i]['resources'] < distance + cells[i]['opp_ants']
            if distance > available_ants:
                goOn = False
                break
            else:
                if cells[i]['type'] == 2 and cells[i]['resources'] > 0:
                    # send ants to crystal
                    commands = insert_in_order(commands, {
                        'type': 'LINE',	
                        'source': nearest_cells_connected_to_base(cells_under_attack, i),
                        'target': i,
                        'strength': 1,
                    })
                    # add to cells_under_attack in first position
                    cells_under_attack.insert(0, i)
                    available_ants -= distance
                elif cells[i]['type'] == 1 and cells[i]['resources'] > 0 and not_enough_eggs:
                    # send ants to eggs
                    commands = insert_in_order(commands, {
                        'type': 'LINE',	
                        'source': nearest_cells_connected_to_base(cells_under_attack, i),
                        'target': i,
                        'strength': 1,
                    })
                    cells_under_attack.insert(0, i)
                    available_ants -= distance
                    egg_taking += cells[i]['resources']
                # add neighs to next_cells if not visited
                for j in cells[i]['neighs']:
                    if j not in visited and j != -1 and j not in current_cells and j not in next_cells:
                        next_cells.append(j)
                
    return commands

def translate_roads_to_commands(roads, cells_under_attack):
    commands = []
    print('cells_under_attack: ', cells_under_attack, file=sys.stderr, flush=True)
    for cell in cells_under_attack:
        print('cell: ', cell, file=sys.stderr, flush=True)
        for r in roads[cell]:
            commands = insert_in_order(commands, {
                'type': 'BEACON',	
                'target': r,
                'strength': 1,
            })
    return commands

def strategy3():
    # if a cell contians crystal or eggs, send ants to it
    road_for_cells =  [[[b] for i in range(number_of_cells)] for b in my_bases]
    r = 0
    available_ants = total_my_ants - len(my_bases)
    visited = []
    next_cells = my_bases
    egg_taking = 0 # egg in the cell under attack
    cells_under_attack = my_bases.copy()
    distance = 0
    while available_ants > 0 and len(next_cells) > 0:
        distance += 1
        not_enough_eggs = egg_taking + total_my_ants < remain_christals / 2
        current_cells = next_cells
        next_cells = []
        for i in current_cells:
            visited.append(i)
            if cells[i]['type'] == 2 and cells[i]['resources'] > 0:
                cells_under_attack.insert(0, i)
                available_ants -= distance
                road_for_cells[r][i].append(i)
            elif cells[i]['type'] == 1 and cells[i]['resources'] > 0 and not_enough_eggs:
                cells_under_attack.insert(0, i)
                available_ants -= distance
                egg_taking += cells[i]['resources']
                road_for_cells[r][i].append(i)
            # add neighs to next_cells if not visited
            for j in cells[i]['neighs']:
                if j not in visited and j != -1 and j not in current_cells and j not in next_cells:
                    next_cells.append(j)
                    road_for_cells[r][j].append(i)  
    commands = translate_roads_to_commands(road_for_cells[r], cells_under_attack)
    return commands


def strategy_egg_near_base():
    # check only base and neightbours for eggs
    commands = []
    available_ants = total_my_ants - len(my_bases)
    visited = []
    next_cells = my_bases
    search_distance = 0
    while available_ants > 0 and len(next_cells) > 0:
        current_cells = next_cells
        next_cells = []
        for i in current_cells:
            visited.append(i)
            if cells[i]['type'] == 1 and cells[i]['resources'] > 0:
                # send ants to eggs
                commands = insert_in_order(commands, {
                    'type': 'LINE',	
                    'source': my_bases[0],
                    'target': i,
                    'strength': 1,
                })
            # add neighs to next_cells if not visited
            if search_distance < 1:
                search_distance += 1
                for j in cells[i]['neighs']:
                    if j not in visited and j != -1 and j not in current_cells and j not in next_cells:
                        next_cells.append(j)
                
    return commands

def strategy2():
    # go to the nearest crystal or egg, eggs have higher priority
    # start from the bases
    commands = []
    for b in my_bases:
        visited = []
        found = False
        next_cells = cells[b]['neighs']
        while len(next_cells) > 0 and not found:
            current_cells = next_cells
            next_cells = []
            for i in current_cells:
                if cells[i]['type'] == 1 and i != -1 and cells[i]['resources'] > 0:
                    commands = insert_in_order(commands, {
                        'type': 'LINE',	
                        'source': b,
                        'target': i,
                        'strength': cells[i]['resources'] * FORCE_STRATEGY_2,
                    })
                    found = True
                elif cells[i]['type'] == 2 and i != -1 and cells[i]['resources'] > 0 and not found:
                    commands = insert_in_order(commands, {
                        'type': 'LINE',	
                        'source': b,
                        'target': i,
                        'strength': cells[i]['resources'] * FORCE_STRATEGY_2,
                    })
                    found = True
                elif i not in visited and i != -1 and not found:
                    # add neighs to next_cells if not visited
                    for j in cells[i]['neighs']:
                        if j not in visited and j != -1:
                            next_cells.append(j)
                visited.append(i)
    # print commands seperated by ;
    return commands
    

# game loop
while True:
    total_my_ants = 0
    total_opp_ants = 0
    turn += 1
    remain_christals = 0
    remain_eggs = 0
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
