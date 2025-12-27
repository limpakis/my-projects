
"""
RLFAP Benchmark Solver

This module runs comprehensive benchmarks on Radio Link Frequency Assignment Problem (RLFAP)
instances using multiple CSP solving algorithms including FC, MAC, FC-CBJ, and Min-Conflicts.

Usage:
    python main.py
    
The script automatically discovers all RLFAP instances in the data/ directory and tests
each algorithm, reporting execution time, assignments, and success/failure.
"""

import os
import time
import glob
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rlfap import RLFAP
from csp import backtracking_search, mac, forward_checking, min_conflicts, dom_wdeg, forward_checking_wdeg, fc_cbj_search, mrv

def get_instances(directory):
    """
    Discover all RLFAP instances in the specified directory.
    
    An RLFAP instance consists of three files with matching names:
    - var*.txt: Variable definitions
    - dom*.txt: Domain definitions  
    - ctr*.txt: Constraint definitions
    
    Args:
        directory (str): Path to directory containing RLFAP instance files
        
    Returns:
        list: Sorted list of dictionaries, each containing:
            - name (str): Instance identifier
            - var (str): Path to variables file
            - dom (str): Path to domains file
            - ctr (str): Path to constraints file
    """
    var_files = glob.glob(os.path.join(directory, "var*.txt"))
    instances = []
    for vf in var_files:
        base = os.path.basename(vf)
        # Αφαιρούμε το 'var' και το '.txt' για να βρούμε το όνομα (π.χ. '11' από 'var11.txt')
        name = base[3:-4]
        dom_file = os.path.join(directory, f"dom{name}.txt")
        ctr_file = os.path.join(directory, f"ctr{name}.txt")
        
        # Έλεγχος αν υπάρχουν τα αντίστοιχα αρχεία
        if os.path.exists(dom_file) and os.path.exists(ctr_file):
            instances.append({
                'name': name,
                'var': vf,
                'dom': dom_file,
                'ctr': ctr_file
            })
    # Ταξινόμηση με βάση το όνομα
    return sorted(instances, key=lambda x: x['name'])

def run_solver(solver_func, problem, name, **kwargs):
    """
    Execute a CSP solver and measure performance metrics.
    
    Args:
        solver_func (callable): The solver function to execute
        problem (CSP): The CSP problem instance
        name (str): Name of the algorithm (for logging)
        **kwargs: Additional arguments to pass to solver
        
    Returns:
        tuple: (success, duration, assignments) where:
            - success (bool): Whether a solution was found
            - duration (float): Execution time in seconds
            - assignments (int): Number of variable assignments made
    """
    start_time = time.time()
    problem.nassigns = 0 # Reset counter
    
    # Reset weights for dom/wdeg
    if hasattr(problem, 'constraint_weights'):
        problem.constraint_weights.clear()
        for v1 in problem.neighbors:
            for v2 in problem.neighbors[v1]:
                edge = tuple(sorted((v1, v2)))
                problem.constraint_weights[edge] = 1
                
    result = solver_func(problem, **kwargs)
    end_time = time.time()
    duration = end_time - start_time
    success = result is not None
    return success, duration, problem.nassigns

def main():
    """
    Main benchmark runner for RLFAP instances.
    
    Discovers all RLFAP instances in the data directory and runs multiple
    CSP algorithms on each, comparing their performance in terms of:
    - Execution time
    - Number of assignments
    - Success rate
    
    Algorithms tested:
    - FC (Forward Checking with dom/wdeg)
    - MAC (Maintaining Arc Consistency)
    - FC-CBJ (Forward Checking with Conflict-Directed Backjumping)
    - MinConflicts (Local Search)
    """
    directory = "../data"  # Data folder
    instances = get_instances(directory)
    
    print(f"{'Instance':<15} | {'Algorithm':<10} | {'Time (s)':<10} | {'Assigns':<10} | {'Result':<10}")
    print("-" * 65)
    
    # Ορισμός των αλγορίθμων που θα τρέξουμε
    algorithms = [
        ("FC", lambda p: backtracking_search(p, select_unassigned_variable=dom_wdeg, inference=forward_checking_wdeg)),
        ("MAC", lambda p: backtracking_search(p, select_unassigned_variable=dom_wdeg, inference=mac)),
        ("FC-CBJ", lambda p: fc_cbj_search(p, select_unassigned_variable=dom_wdeg)),
    ]

    for inst in instances:
        print(f"Running instance: {inst['name']}")
        
        # Φόρτωση προβλήματος
        try:
            problem = RLFAP(inst['var'], inst['dom'], inst['ctr'])
        except Exception as e:
            print(f"Error loading {inst['name']}: {e}")
            continue
        
        for alg_name, alg_func in algorithms:
            try:
                # Εδώ θα μπορούσαμε να βάλουμε timeout
                success, duration, assigns = run_solver(alg_func, problem, alg_name)
                print(f"{inst['name']:<15} | {alg_name:<10} | {duration:<10.4f} | {assigns:<10} | {'Solved' if success else 'Failed':<10}")
            except Exception as e:
                print(f"{inst['name']:<15} | {alg_name:<10} | {'Error':<10} | {'-':<10} | {str(e):<10}")
        
        # Δοκιμή MinConflicts για δύσκολα instances (π.χ. αν αποτύχουν τα άλλα ή πάρουν πολύ χρόνο)
        # Για την άσκηση το τρέχουμε πάντα ή επιλεκτικά. Ας το τρέξουμε.
        print(f"Running MinConflicts for {inst['name']}...")
        try:
            success, duration, assigns = run_solver(lambda p: min_conflicts(p, max_steps=1000), problem, "MinConflicts")
            print(f"{inst['name']:<15} | {'MinConfl':<10} | {duration:<10.4f} | {assigns:<10} | {'Solved' if success else 'Failed':<10}")
        except Exception as e:
            print(f"MinConflicts Error: {e}")

        print("-" * 65)

if __name__ == "__main__":
    main()
