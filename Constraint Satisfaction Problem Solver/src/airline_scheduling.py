"""
Airline Crew Pairing Scheduling using CSP techniques.
Solves the Set Cover problem to minimize crew pairing costs.
"""

import os
import sys
import time

class AirlineScheduler:
    def __init__(self, filename):
        self.filename = filename
        self.N = 0
        self.M = 0
        self.pairings = [] # List of (cost, set_of_flights, original_index)
        self.flight_to_pairings = {} # Map flight_id -> list of pairing indices
        self.best_solution = None
        self.best_cost = float('inf')
        self.nodes_visited = 0
        
        self.load_data()

    def load_data(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            
        # Parse header
        header = lines[0].split()
        self.N = int(header[0])
        self.M = int(header[1])
        
        # Parse pairings
        for i, line in enumerate(lines[1:]):
            parts = list(map(int, line.split()))
            cost = parts[0]
            num_flights = parts[1]
            flights = set(parts[2:])
            
            if len(flights) != num_flights:
                # Sanity check, though input is assumed correct
                pass
                
            self.pairings.append({
                'id': i + 1,
                'cost': cost,
                'flights': flights
            })
            
        # Build index
        for f in range(1, self.N + 1):
            self.flight_to_pairings[f] = []
            
        for i, p in enumerate(self.pairings):
            for f in p['flights']:
                self.flight_to_pairings[f].append(i)
                
        # Sort pairings for each flight by cost (heuristic)
        for f in range(1, self.N + 1):
            self.flight_to_pairings[f].sort(key=lambda idx: self.pairings[idx]['cost'])

    def solve(self):
        self.best_solution = None
        self.best_cost = float('inf')
        self.nodes_visited = 0
        
        start_time = time.time()
        
        # Initial state
        uncovered_flights = set(range(1, self.N + 1))
        current_solution = []
        current_cost = 0
        
        self._backtrack(uncovered_flights, current_solution, current_cost)
        
        end_time = time.time()
        return {
            'cost': self.best_cost,
            'solution': [self.pairings[i]['id'] for i in self.best_solution] if self.best_solution else None,
            'time': end_time - start_time,
            'nodes': self.nodes_visited
        }

    def _backtrack(self, uncovered_flights, current_solution, current_cost):
        self.nodes_visited += 1
        
        # Pruning
        if current_cost >= self.best_cost:
            return

        # Base case: all flights covered
        if not uncovered_flights:
            if current_cost < self.best_cost:
                self.best_cost = current_cost
                self.best_solution = list(current_solution)
            return

        # Heuristic: Pick the flight with the fewest available pairings (MRV - Minimum Remaining Values)
        # This drastically reduces the branching factor
        # Also, if any flight has 0 options, we can backtrack immediately
        best_flight = -1
        min_options = float('inf')
        
        sorted_uncovered = sorted(list(uncovered_flights)) # Deterministic order
        
        for f in sorted_uncovered:
            # Count valid pairings for this flight
            # A pairing is valid if it doesn't overlap with already covered flights (which are NOT in uncovered_flights)
            # Actually, we just need to check if the pairing is compatible with the current state.
            # But here, we are building constructively.
            # The pairings in flight_to_pairings[f] are candidates.
            # We need to check if all flights in a candidate pairing are currently uncovered.
            
            valid_count = 0
            for p_idx in self.flight_to_pairings[f]:
                p_flights = self.pairings[p_idx]['flights']
                if p_flights.issubset(uncovered_flights):
                    valid_count += 1
            
            if valid_count == 0:
                return # Dead end: this flight cannot be covered
            
            if valid_count < min_options:
                min_options = valid_count
                best_flight = f
                if min_options == 1:
                    break # Can't get better than 1
        
        # Branch on the chosen flight
        # Try all pairings that cover 'best_flight' and are valid
        candidates = []
        for p_idx in self.flight_to_pairings[best_flight]:
            p_flights = self.pairings[p_idx]['flights']
            if p_flights.issubset(uncovered_flights):
                candidates.append(p_idx)
        
        # Sort candidates? Maybe by cost density?
        # Already sorted by cost in __init__, but maybe cost per flight is better?
        # Let's stick to simple cost for now.
        
        for p_idx in candidates:
            pairing = self.pairings[p_idx]
            
            # Forward step
            new_uncovered = uncovered_flights - pairing['flights']
            current_solution.append(p_idx)
            
            self._backtrack(new_uncovered, current_solution, current_cost + pairing['cost'])
            
            # Backtrack
            current_solution.pop()

def main():
    # Check if pairings directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pairings_dir = os.path.join(base_dir, 'pairings')
    
    if not os.path.exists(pairings_dir):
        print(f"Directory {pairings_dir} not found.")
        return

    files = sorted([f for f in os.listdir(pairings_dir) if f.endswith('.txt') and f != 'format.txt'])
    
    print(f"{'Instance':<15} | {'Cost':<10} | {'Time (s)':<10} | {'Nodes':<10} | {'Solution'}")
    print("-" * 80)
    
    for filename in files:
        filepath = os.path.join(pairings_dir, filename)
        solver = AirlineScheduler(filepath)
        result = solver.solve()
        
        sol_str = str(result['solution'])
        if len(sol_str) > 30:
            sol_str = sol_str[:27] + "..."
            
        print(f"{filename:<15} | {result['cost']:<10} | {result['time']:<10.4f} | {result['nodes']:<10} | {sol_str}")

if __name__ == "__main__":
    main()
