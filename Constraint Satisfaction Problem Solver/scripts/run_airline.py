import os
import sys
import glob

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from airline_scheduling import AirlineScheduler

def run_all():
    pairings_dir = '/Users/sotirioslympakis/Downloads/pairings'
    files = sorted(glob.glob(os.path.join(pairings_dir, '*.txt')))
    
    print(f"{'Instance':<15} | {'Cost':<10} | {'Time (s)':<10} | {'Nodes':<10}")
    print("-" * 55)
    
    results = []

    for file_path in files:
        filename = os.path.basename(file_path)
        if filename == 'format.txt':
            continue
            
        scheduler = AirlineScheduler(file_path)
        result = scheduler.solve()
        
        print(f"{filename:<15} | {result['cost']:<10} | {result['time']:<10.4f} | {result['nodes']:<10}")
        results.append((filename, result))

if __name__ == "__main__":
    run_all()
