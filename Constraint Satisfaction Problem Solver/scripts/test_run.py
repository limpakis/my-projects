
import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rlfap import RLFAP
from csp import backtracking_search, dom_wdeg, forward_checking_wdeg, fc_cbj_search, min_conflicts

def test():
    print("Testing RLFAP solver...")
    # Try smaller instances first
    test_instances = ['var11.txt', 'var6-w2.txt', 'var3-f10.txt']
    
    for var_file in test_instances:
        if os.path.exists(f'../data/{var_file}'):
            instance_name = var_file.replace('var', '').replace('.txt', '')
            dom_file = f'../data/dom{instance_name}.txt'
            ctr_file = f'../data/ctr{instance_name}.txt'
            
            if os.path.exists(dom_file) and os.path.exists(ctr_file):
                print(f"\n--- Testing instance {instance_name} ---")
                try:
                    problem = RLFAP(f'../data/{var_file}', dom_file, ctr_file)
                    print(f"Problem loaded successfully.")
                    print(f"Variables: {len(problem.variables)}")
                    print(f"Constraints: {len([c for constraints in problem.constraints_map.values() for c in constraints])//2}")
                    # Check first variable domain
                    first_var = problem.variables[0]
                    domain_str = str(problem.domains[first_var])
                    if len(domain_str) > 80:
                        domain_str = domain_str[:77] + "..."
                    print(f"Domain of var {first_var}: {domain_str}")
                    
                    # Quick test with timeout-like behavior (limit assignments)
                    print("Running FC with dom/wdeg...")
                    start = time.time()
                    problem.nassigns = 0
                    result = backtracking_search(problem, select_unassigned_variable=dom_wdeg, inference=forward_checking_wdeg)
                    duration = time.time() - start
                    print(f"FC Result: {'Solved' if result else 'Failed'} in {duration:.2f}s, {problem.nassigns} assignments")
                    
                    if result and len(problem.variables) <= 50:  # Only show solution for small instances
                        print(f"Sample solution (first 5): {dict(list(result.items())[:5])}")
                        
                    break  # Test only one successful instance
                except Exception as e:
                    print(f"Error with {instance_name}: {e}")
                    continue
    
    print("\nTest completed!")

if __name__ == "__main__":
    test()
