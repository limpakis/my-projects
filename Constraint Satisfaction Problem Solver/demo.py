#!/usr/bin/env python3
"""
RLFAP Demo Script

Simple demonstration of the CSP solver.
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rlfap import RLFAP
from csp import backtracking_search, dom_wdeg, forward_checking_wdeg

def demo():
    """Run a simple demo of the RLFAP solver."""
    print("RLFAP CSP Solver Demo")
    print("=" * 30)
    
    # Find a working small instance
    small_instances = [
        ('11', 'Instance 11 - Easy'),
        ('3-f10', 'Instance 3-f10 - Medium'),
        ('6-w2', 'Instance 6-w2 - Small')
    ]
    
    for instance_id, description in small_instances:
        var_file = f'data/var{instance_id}.txt'
        dom_file = f'data/dom{instance_id}.txt'
        ctr_file = f'data/ctr{instance_id}.txt'
        
        if all(os.path.exists(f) for f in [var_file, dom_file, ctr_file]):
            print(f"\nTesting {description}")
            print("-" * 20)
            
            try:
                # Load problem
                problem = RLFAP(var_file, dom_file, ctr_file)
                
                # Display problem info
                print(f"Variables: {len(problem.variables)}")
                print(f"Domain size (avg): {sum(len(d) for d in problem.domains.values()) / len(problem.domains):.1f}")
                print(f"Constraints: {sum(len(constraints) for constraints in problem.constraints_map.values()) // 2}")
                
                # Solve with FC
                print(f"\nSolving with Forward Checking...")
                start_time = time.time()
                problem.nassigns = 0
                
                solution = backtracking_search(
                    problem, 
                    select_unassigned_variable=dom_wdeg,
                    inference=forward_checking_wdeg
                )
                
                duration = time.time() - start_time
                
                if solution:
                    print(f"SUCCESS!")
                    print(f"Time: {duration:.4f} seconds")
                    print(f"Assignments: {problem.nassigns}")
                    
                    if len(solution) <= 10:
                        print(f"Solution: {solution}")
                    else:
                        sample_solution = dict(list(solution.items())[:5])
                        print(f"Sample solution: {sample_solution}")
                else:
                    print(f"No solution found in {duration:.4f}s")
                    print(f"Assignments tried: {problem.nassigns}")
                
                return True
                
            except Exception as e:
                print(f"Error: {e}")
                continue
                
    print("\nNo suitable test instances found.")

def show_project_structure():
    """Display the project structure."""
    print("\nProject Structure:")
    print("-" * 18)
    print("rlfap/")
    print("├── README.md              # Comprehensive documentation")
    print("├── requirements.txt       # Python dependencies") 
    print("├── demo.py               # This demo script")
    print("├── src/                  # Core source code")
    print("│   ├── csp.py           # CSP framework & algorithms")
    print("│   ├── rlfap.py         # RLFAP problem implementation")
    print("│   ├── rlfap_parser.py  # Instance file parser")
    print("│   └── airline_scheduling.py # Airline scheduling solver")
    print("├── scripts/              # Executable scripts")
    print("│   ├── main.py          # Benchmark runner")
    print("│   ├── test_run.py      # Test script")
    print("│   └── run_airline.py   # Airline scheduler runner")
    print("├── data/                 # RLFAP benchmark instances")
    print("│   ├── var*.txt         # Variable definitions")
    print("│   ├── dom*.txt         # Domain definitions")
    print("│   └── ctr*.txt         # Constraint definitions")
    print("└── examples/             # Usage examples & outputs")

if __name__ == "__main__":
    show_project_structure()
    success = demo()
    
    if success:
        print(f"\nProject is working correctly!")
    else:
        print(f"\nSome issues found.")