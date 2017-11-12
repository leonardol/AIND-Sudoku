assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminates the values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Finds all instances of naked twins
    # Eliminates the naked twins as possibilities for their peers
    
    
    couples = {}
    for unit in unitlist:
        couples = {}
        for i in range(len(unit)-1):
            for j in range(i+1, len(unit)):
                if len(values[unit[i]]) == 2 and values[unit[i]] == values[unit[j]]:
                    couples[values[unit[i]]] = 1
        twins = [c for c in couples if couples[c] == 1]
        for u in unit:
            for t in twins:
                if values[u] != t:
                    for c in t:
                        if c in values[u]:
                            assign_value(values,u,values[u].replace(c, ''))
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
boxes = cross(rows, cols)
rowunits = [cross(r, cols) for r in rows]
colunits = [cross(rows, c) for c in cols]
squareunits = [cross(e, f) for e in ('ABC', 'DEF', 'GHI') for f in ('123', '456', '789')]

# The diagunits variable groups in two units the diagonals of the board.
# This further tight constraint narrow the possibilities for the solution
# only in the case of diagonal sudokus. No solution instead is provided in
# other types of sudokus.
diagunits = [sum([cross(r,c) for r, c in zip(rows,cols)],[])]+ [sum([cross(r,c) for r, c in zip(rows,reversed(cols))],[])]


unitlist = rowunits + colunits + squareunits + diagunits
units = dict((s,[u for u in unitlist if s in u]) for s in boxes)
peers = dict((s,[set(sum(units[s],[])) - set([s])]) for s in boxes)

def grid_values(grid):
    """
    Converts grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81   
    values = {}
    for box,g in zip(boxes,grid):
        if g not in digits:
            values[box] = digits
        else:
            values[box] = g    
    return values

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[box]) for box in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF':
            print(line)    

def eliminate(values):
    """Eliminates values from peers of each box with a single value.

    Goes through all the boxes, and whenever there is a box with a single value,
    eliminates this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    
    single_value_boxes = [box for box in boxes if len(values[box]) == 1]
    for box in single_value_boxes:
        for box_peers in peers[box]:
            for peer in box_peers:
                if values[box] in values[peer]:
                    assign_value(values, peer, values[peer].replace(values[box], '')) 
    return values
                    
    

def only_choice(values):
    """Finalizes all values that are the only choice for a unit.

    Goes through all the units, and whenever there is a unit with a value
    that only fits in one box, assigns the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    
    for unit in unitlist:
        for digit in digits:
            count = 0
            for u in unit:
                if digit in values[u]:
                    pos = u
                    count += 1
            if count == 1:
                assign_value(values, pos, digit)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Checks how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Uses the Eliminate Strategy
        values  = eliminate(values)

        # Uses the Only Choice Strategy
        values = only_choice(values)
        
        # Uses the Naked Twins Strategy
        values = naked_twins(values)


        # Checks how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stops the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, returns False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, creates a search tree and solve the sudoku."
    # First, reduces the puzzle using the previous function
    values = reduce_puzzle(values)
    if values:
        if len([box for box in values.keys() if len(values[box]) > 1]) == 0:
            return values
    else:
        return values
    # Chooses one of the unfilled squares with the fewest possibilities
    min = 10
    pos = ''
    for box in values.keys():
        if len(values[box]) < min and len(values[box]) > 1:
            min = len(values[box])
            pos = box

    # Now uses recursion to solve each one of the resulting sudokus, and if one returns a value (not False), returns that answer!
    for c in values[pos]:
        new_sudoku = values.copy()
        new_sudoku[pos] = c
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Finds the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    
    # Uses the Search Strategy
    values = search(values)

    if not values or len([box for box in values.keys() if len(values[box]) > 1]) != 0:
        return False
    return values
    
if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
