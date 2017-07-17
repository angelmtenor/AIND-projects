"""
Solve a Sudoku with AI
Artificial Intelligence Nanodegree Program - Udacity

The data consists of a text file of diagonal sudokus for you to solve.

"""


def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Input: values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Output: the values dictionary with the naked twins eliminated from peers.
    """
    two_digit_boxes = [box for box in values.keys() if len(values[box]) == 2]
    # each two_digit_boxes searches for a twin among its peers
    for box in two_digit_boxes:
        for peer in peers[box]:
            if values[peer] == values[box]:
                # pair of naked twins found
                # getting its shared units:  usually one, although more is possible ( missing in the test! )
                shared_units = [x for x in units[box] if x in units[peer]]
                # For each cell in each shared unit, remove the two digits of the naked twins (except for the twins)
                for shared_unit in shared_units:
                    for b in shared_unit:
                        if b != box and b != peer:
                            for digit in values[box]:
                                value = values[b].replace(digit, '')
                                values[b] = value
    return values


def naked_triplets(values):  # Improvement
    """
    Eliminate values using the naked triplets strategy.
    Input: values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Output: the values dictionary with the naked triplets eliminated from peers.
    """
    three_digit_boxes = [box for box in values.keys() if len(values[box]) == 3]
    # each 3_digit_boxes searches for 2 TWINS among its peers
    for box in three_digit_boxes:
        for peer in peers[box]:
            if values[peer] == values[box]:
                # pair of twins found
                # getting its shared units:  usually one, although more is possible
                shared_units = [x for x in units[box] if x in units[peer]]
                for shared_unit in shared_units:
                    for b in shared_unit:
                        if b != box and b != peer:
                            if values[b] == values[box]:
                                # triplet found !!
                                # Multiple shared unit here are still possible. Above shared_unit loops also resolves
                                #  this special case here.
                                for c in shared_unit:
                                    # For each cell in each shared unit, remove the three digits of the naked triplets
                                    if c != box and c != peer and c != b:
                                        for digit in values[box]:
                                            value = values[c].replace(digit, '')
                                            values[c] = value
    return values


def cross(a, b):
    """
    Input:  a, b (string, tuple, list .. )
    Output: cross list of all elements of a combined with b.
            Example: a='AB', b = '12' -> ['A1', 'A2', 'B1', 'B2']
    """
    return [s + t for s in a for t in b]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input:  grid(string) - A grid in string form.
    Output: A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    values = dict(zip(boxes, grid))

    # replace "." in the dictionary
    for key, value in values.items():
        if value == ".":
            value = "123456789"
        values[key] = value
    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Input:  values(dict): The sudoku in dictionary form
    """
    for k, v in values.items():
        if len(v) > 1:
            values[k] = " "

    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its
     peers.
    Input:  A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    # get solved boxes (1 value)
    solved = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved:
        for peer in peers[box]:
            # eliminate solved value from peers (if possible)
            value = values[peer].replace(values[box], '')
            values[peer] = value
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to
     this box.
    Input:  A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            # boxes per unit holding a particular digit
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                # Just 1 box has the digit in its values for this unit -> only choice
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice(), and naked_twins().
    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of all the functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Eliminate Strategy
        values = eliminate(values)
        # Only Choice Strategy
        values = only_choice(values)
        # Naked Twins Strategy
        values = naked_twins(values)
        # Naked Triplets Strategy.   # Uncomment
        # values = naked_triplets(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """
    Using depth-first search and propagation, try all possible values
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form or False if there is a box with zero available values
    """

    # reduce the puzzle
    values = reduce_puzzle(values)
    if values is False:  # Unsolved (zero available values)
        return False
    if all(len(values[s]) == 1 for s in boxes):  # Solved
        return values

    # choose one of the unfilled squares with the fewest possibilities
    _, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # solve recursively each one of the resulting sudokus; if one returns a value (not False), return the answer
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Input:  grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Output: The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


# Constants used
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [[r + c for r, c in zip(rows, cols)], [r + c for r, c in zip(rows, cols[::-1])]]
# [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    print("\n  Sudoku:\n")
    display(grid_values(diag_sudoku_grid))

    solution = solve(diag_sudoku_grid)

    if(solution):
        print("\n  Solution found: \n")
    else:
        print("\n  Solution not found: \n")

    display(solution)
