from z3 import *
import json
import numpy as np
import matplotlib.pyplot as plt

import re

with open('/Users/eeshnaugraiya/Desktop/sudoku/input.json', 'r') as f:
        data = json.load(f)

for input_data in data:

    instance = input_data['instance']
    p = input_data['p']
    q = input_data['q']
    val = input_data['val']


    instance[p][q]=0

    X = [[Int("x_%s_%s" % (i, j)) for i in range(9)] for j in range(9)]

    cells_c = [And(1 <= X[i][j], X[i][j] <= 9) for i in range(9) for j in range(9)]
    rows_c = [Distinct(X[i]) for i in range(9)]
    cols_c = [Distinct([X[i][j] for i in range(9)]) for j in range(9)]
    sq_c = [Distinct([X[3 * i0 + i][3 * j0 + j] for j in range(3) for i in range(3)])
                for j0 in range(3) for i0 in range(3)]
    instance_c=[]
    
    for i in range(9):
        for j in range(9):
            if instance[i][j] != 0:
                instance_c.append(X[i][j] == instance[i][j])

    flip = [Not(X[p][q] == val)]
    constraints = cells_c + rows_c + cols_c + sq_c + instance_c + flip
    s= Solver()

    sudoku_rules = rows_c + cols_c + sq_c
    constraints = []
    for i in sudoku_rules:
        s.assert_and_track(i, "sudoku_rules_" + str(i))
    for i in instance_c: 
        s.assert_and_track(i, "Value_cons_" + str(i))
    s.add(flip)

    s.add(cells_c)



    s.set(':core.minimize', True)
    s.set(':unsat-core', True)
    res = s.check()
    if res == z3.sat:
        print("Problem")
        exit()
    elif res == z3.unsat:
        core = [str(c) for c in s.unsat_core()]  
    
        instance_core = [str(c) for c in core if "Value_cons_" in str(c)]
        sudoku_core = [str(c) for c in core if "sudoku_rules_" in str(c)]



    formatted_constraints = []
    for constraint in instance_core:
        parts = constraint.split(" == ")
        variable_parts = parts[0].split("_")
        i, j = int(variable_parts[3]), int(variable_parts[4])
        value = int(parts[1])
        formatted_constraints.append(f"X[{i}][{j}] == {value}")
    print(len(formatted_constraints))

  
    pattern = r"x_(\d+)_(\d+)"

    # Create a set to store the indices
    indices = set()

    # Loop through each string in the data
    for string in sudoku_core:
        # Find all matches of the pattern in the string
        matches = re.findall(pattern, string)
        # Extract indices from each match and add to the set
        for match in matches:
            indices.add((int(match[0]), int(match[1])))

    # Convert set to list for further processing if needed
    indices = list(indices)

    print(len(indices))

  
    sudoku_solution = np.zeros((9, 9), dtype=int)

    # Fill the grid with the solution
    for constraint in formatted_constraints:
        match = re.search(r"X\[(\d+)\]\[(\d+)\] == (\d+)", constraint)
        if match:
            i, j, value = map(int, match.groups())
            sudoku_solution[i][j] = value



    highlight_constraint = f"X[{q}][{p}] == {val}"

    highlight_match = re.search(r"X\[(\d+)\]\[(\d+)\] == (\d+)", highlight_constraint)
    if highlight_match:
        i, j, value = map(int, highlight_match.groups())
        sudoku_solution[i][j] = value
    if highlight_match:
        plt.text(j, i, str(value), ha='center', va='center', fontsize=12, color='red', weight='bold')
        


    

    # Create custom colormap
    cmap = plt.get_cmap('viridis')
    cmap.set_under('white')

    # Plot Sudoku grid
    plt.imshow(sudoku_solution, cmap=cmap, origin='upper', vmin=0.1)
    plt.colorbar()
    plt.title("Sudoku Grid based on Formatted Constraints")

    # Add numbers to each cell
    for i in range(9):
        for j in range(9):
            if sudoku_solution[i][j] != 0:
                plt.text(j, i, str(int(sudoku_solution[i][j])), ha='center', va='center', fontsize=12, color='black') 

   

        

    formatted_constraints.append(highlight_constraint) 
    formatted_constraints_string = ' '.join(formatted_constraints)
    for index in indices:
        if f"X[{index[0]}][{index[1]}]" not in formatted_constraints_string:
            plt.fill([index[1] - 0.5, index[1] + 0.5, index[1] + 0.5, index[1] - 0.5], 
                    [index[0] - 0.5, index[0] - 0.5, index[0] + 0.5, index[0] + 0.5], 'gray')

        
    # Add gridlines
    for i in range(4):
        plt.axhline(y=i * 3 - 0.5, color='black', linewidth=2)  # Horizontal lines
        plt.axvline(x=i * 3 - 0.5, color='black', linewidth=2)  # Vertical lines

    plt.xticks(np.arange(9)-0.5, np.arange(1, 10))
    plt.yticks(np.arange(9)-0.5, np.arange(1, 10))
    plt.grid(color='black', linewidth=1)
    plt.savefig(f"graph_{p}_{q}_{val}.png")
    plt.show()
    


    