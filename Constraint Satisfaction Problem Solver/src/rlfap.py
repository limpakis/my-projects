
"""RLFAP (Radio Link Frequency Assignment Problem) implementation."""

from csp import CSP
from collections import defaultdict
from rlfap_parser import parse_domains, parse_variables, parse_constraints

class RLFAP(CSP):
    def __init__(self, var_file, dom_file, ctr_file):
        # Φόρτωση δεδομένων
        raw_domains = parse_domains(dom_file)
        self.var_domains = parse_variables(var_file, raw_domains)
        parsed_constraints = parse_constraints(ctr_file)

        variables = list(self.var_domains.keys())
        domains = self.var_domains
        
        # Κατασκευή γράφου γειτόνων και λεξικού περιορισμών
        neighbors = defaultdict(list)
        self.constraints_map = defaultdict(list)

        for v1, v2, op, k in parsed_constraints:
            neighbors[v1].append(v2)
            neighbors[v2].append(v1)
            
            # Αποθηκεύουμε τον περιορισμό και για τις δύο κατευθύνσεις
            # Η μορφή είναι |x - y| > k
            self.constraints_map[(v1, v2)].append((op, k))
            self.constraints_map[(v2, v1)].append((op, k))

        # Αρχικοποίηση της κλάσης CSP
        super().__init__(variables, domains, neighbors, self.constraint_check)
        
        # Για το dom/wdeg heuristic
        # Αρχικοποιούμε τα βάρη των περιορισμών (ακμών) σε 1
        self.constraint_weights = defaultdict(lambda: 1)
        for v1 in neighbors:
            for v2 in neighbors[v1]:
                # Χρησιμοποιούμε ταξινομημένο tuple για να είναι μοναδικό το κλειδί για κάθε ακμή
                edge = tuple(sorted((v1, v2)))
                self.constraint_weights[edge] = 1

    def constraint_check(self, A, a, B, b):
        """
        Ελέγχει αν ικανοποιούνται όλοι οι περιορισμοί μεταξύ A=a και B=b.
        """
        # Αν δεν υπάρχουν περιορισμοί, όλα καλά
        if (A, B) not in self.constraints_map:
            return True
            
        for op, k in self.constraints_map[(A, B)]:
            diff = abs(a - b)
            if op == '>':
                if not (diff > k):
                    return False
            elif op == '=':
                if not (diff == k):
                    return False
            # Μπορούμε να προσθέσουμε κι άλλους τελεστές αν χρειαστεί
        return True
