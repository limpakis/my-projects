
# filepath: /Users/sotirioslympakis/Desktop/Texniti Noimosinh/rlfap/csp.py
"""CSP (Constraint Satisfaction Problems) problems and solvers. (Chapter 6)"""

import itertools
import random
import re
import string
from collections import defaultdict, Counter
from functools import reduce
from operator import eq, neg

from sortedcontainers import SortedSet


def argmin_random_tie(seq, key):
    """Return a minimum element of seq; break ties at random."""
    return min(seq, key=key)


def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(map(bool, seq))


def first(iterable, default=None):
    """Return the first element of an iterable; or default."""
    try:
        return next(iter(iterable))
    except StopIteration:
        return default


def extend(d, var, val):
    """Copy dict d and extend it by setting var to val; return copy."""
    d2 = d.copy()
    d2[var] = val
    return d2


class CSP:
    """This class describes finite-domain Constraint Satisfaction Problems."""

    def __init__(self, variables, domains, neighbors, constraints):
        """Construct a CSP problem. If variables is empty, it becomes domains.keys()."""
        variables = variables or list(domains.keys())
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.curr_domains = None
        self.nassigns = 0

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment."""
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""
        def conflict(var2):
            return var2 in assignment and not self.constraints(var, val, var2, assignment[var2])

        return count(conflict(v) for v in self.neighbors[var])

    def display(self, assignment):
        """Show a human-readable representation of the CSP."""
        print(assignment)

    def actions(self, state):
        """Return a list of applicable actions: non conflicting
        assignments to an unassigned variable."""
        if len(state) == len(self.variables):
            return []
        else:
            assignment = dict(state)
            var = first([v for v in self.variables if v not in assignment])
            return [(var, val) for val in self.domains[var]
                    if self.nconflicts(var, val, assignment) == 0]

    def result(self, state, action):
        """Perform an action and return the new state."""
        (var, val) = action
        return state + ((var, val),)

    def goal_test(self, state):
        """The goal is to assign all variables, with all constraints satisfied."""
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    def support_pruning(self):
        """Make sure we can prune values from domains."""
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """Start accumulating inferences from assuming var=value."""
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        """Rule out var=value."""
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        """Return all values for var that aren't currently ruled out."""
        return (self.curr_domains or self.domains)[var]

    def infer_assignment(self):
        """Return the partial assignment implied by the current inferences."""
        self.support_pruning()
        return {v: self.curr_domains[v][0]
                for v in self.variables if 1 == len(self.curr_domains[v])}

    def restore(self, removals):
        """Undo a supposition and all inferences from it."""
        for B, b in removals:
            self.curr_domains[B].append(b)

    def conflicted_vars(self, current):
        """Return a list of variables in current assignment that are in conflict"""
        return [var for var in self.variables
                if self.nconflicts(var, current[var], current) > 0]


# ______________________________________________________________________________
# Constraint Propagation with AC3


def dom_j_up(csp, queue):
    return SortedSet(queue, key=lambda t: neg(len(csp.curr_domains[t[1]])))


def AC3(csp, queue=None, removals=None, arc_heuristic=dom_j_up):
    """[Figure 6.3]"""
    if queue is None:
        queue = {(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]}
    csp.support_pruning()
    queue = arc_heuristic(csp, queue)
    checks = 0
    while queue:
        (Xi, Xj) = queue.pop()
        revised, checks = revise(csp, Xi, Xj, removals, checks)
        if revised:
            if not csp.curr_domains[Xi]:
                return False, checks
            for Xk in csp.neighbors[Xi]:
                if Xk != Xj:
                    queue.add((Xk, Xi))
    return True, checks


def revise(csp, Xi, Xj, removals, checks=0):
    """Return true if we remove a value."""
    revised = False
    for x in csp.curr_domains[Xi][:]:
        conflict = True
        for y in csp.curr_domains[Xj]:
            if csp.constraints(Xi, x, Xj, y):
                conflict = False
            checks += 1
            if not conflict:
                break
        if conflict:
            csp.prune(Xi, x, removals)
            revised = True
    return revised, checks


# ______________________________________________________________________________
# CSP Backtracking Search


def first_unassigned_variable(assignment, csp):
    """The default variable order."""
    return first([var for var in csp.variables if var not in assignment])


def mrv(assignment, csp):
    """Minimum-remaining-values heuristic."""
    return argmin_random_tie([v for v in csp.variables if v not in assignment],
                             key=lambda var: num_legal_values(csp, var, assignment))


def num_legal_values(csp, var, assignment):
    if csp.curr_domains:
        return len(csp.curr_domains[var])
    else:
        return count(csp.nconflicts(var, val, assignment) == 0 for val in csp.domains[var])


def unordered_domain_values(var, assignment, csp):
    """The default value order."""
    return csp.choices(var)


def lcv(var, assignment, csp):
    """Least-constraining-values heuristic."""
    return sorted(csp.choices(var), key=lambda val: csp.nconflicts(var, val, assignment))


def no_inference(csp, var, value, assignment, removals):
    return True


def forward_checking(csp, var, value, assignment, removals):
    """Prune neighbor values inconsistent with var=value."""
    csp.support_pruning()
    for B in csp.neighbors[var]:
        if B not in assignment:
            for b in csp.curr_domains[B][:]:
                if not csp.constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                return False
    return True


def mac(csp, var, value, assignment, removals):
    """Maintain arc consistency."""
    return AC3(csp, {(X, var) for X in csp.neighbors[var]}, removals)


def backtracking_search(csp, select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values, inference=no_inference):
    """[Figure 6.5]"""

    def backtrack(assignment):
        if len(assignment) == len(csp.variables):
            return assignment
        var = select_unassigned_variable(assignment, csp)
        for value in order_domain_values(var, assignment, csp):
            if 0 == csp.nconflicts(var, value, assignment):
                csp.assign(var, value, assignment)
                removals = csp.suppose(var, value)
                if inference(csp, var, value, assignment, removals):
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                csp.restore(removals)
        csp.unassign(var, assignment)
        return None

    result = backtrack({})
    assert result is None or csp.goal_test(result)
    return result


def min_conflicts(csp, max_steps=100000):
    """Solve a CSP by stochastic Hill Climbing on the number of conflicts."""
    csp.current = current = {}
    for var in csp.variables:
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)
    for i in range(max_steps):
        conflicted = csp.conflicted_vars(current)
        if not conflicted:
            return current
        var = random.choice(conflicted)
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)
    return None


def min_conflicts_value(csp, var, current):
    """Return the value that will give var the least number of conflicts."""
    return argmin_random_tie(csp.domains[var], key=lambda val: csp.nconflicts(var, val, current))

# ______________________________________________________________________________
# Custom Implementations for RLFAP

def dom_wdeg(assignment, csp):
    """
    Variable ordering heuristic: dom/wdeg.
    Επιλέγει τη μεταβλητή με τον μικρότερο λόγο μεγέθους πεδίου προς το weighted degree.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    
    def ratio(var):
        # Μέγεθος τρέχοντος πεδίου
        dom_size = len(csp.curr_domains[var]) if csp.curr_domains else len(csp.domains[var])
        
        # Υπολογισμός weighted degree
        wdeg = 0
        for neighbor in csp.neighbors[var]:
            if neighbor not in assignment:
                # Ανάκτηση βάρους από το CSP αντικείμενο
                edge = tuple(sorted((var, neighbor)))
                if hasattr(csp, 'constraint_weights'):
                    wdeg += csp.constraint_weights[edge]
                else:
                    wdeg += 1
        
        if wdeg == 0:
            return float('inf')
        return dom_size / wdeg

    return argmin_random_tie(unassigned, key=ratio)

def forward_checking_wdeg(csp, var, value, assignment, removals):
    """
    Forward checking που ενημερώνει τα βάρη των περιορισμών σε περίπτωση DWO.
    """
    csp.support_pruning()
    for B in csp.neighbors[var]:
        if B not in assignment:
            for b in csp.curr_domains[B][:]:
                if not csp.constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                # Domain Wipeout (DWO)
                # Αυξάνουμε το βάρος του περιορισμού (var, B)
                if hasattr(csp, 'constraint_weights'):
                    edge = tuple(sorted((var, B)))
                    csp.constraint_weights[edge] += 1
                return False
    return True

def fc_cbj_search(csp, select_unassigned_variable=dom_wdeg, order_domain_values=unordered_domain_values):
    """
    Forward Checking with Conflict-Directed Backjumping (FC-CBJ).
    """
    # Conflict sets: {var: set of variables that caused reduction in domain}
    conf_set = {v: set() for v in csp.variables}
    
    # Stack to keep track of assignment order for jumping back
    # Actually, we can just use the assignment dict keys if they are ordered (Python 3.7+)
    # But let's be explicit if needed.
    
    def check_forward(var, assignment, removals):
        """
        Εκτελεί FC και ενημερώνει τα conflict sets.
        """
        csp.support_pruning()
        for B in csp.neighbors[var]:
            if B not in assignment:
                for b in csp.curr_domains[B][:]:
                    if not csp.constraints(var, assignment[var], B, b):
                        csp.prune(B, b, removals)
                        # Προσθήκη του var στο conflict set του B
                        conf_set[B].add(var)
                
                if not csp.curr_domains[B]:
                    # DWO στο B
                    # Επιστρέφουμε το B για να ξέρουμε ποιος άδειασε
                    return False, B
        return True, None

    def backtrack(assignment):
        if len(assignment) == len(csp.variables):
            return assignment, None

        var = select_unassigned_variable(assignment, csp)
        
        # Καθαρισμός conflict set για τη νέα μεταβλητή (αν και θα έπρεπε να είναι ήδη σωστό από τα προηγούμενα)
        # conf_set[var] περιέχει ήδη τους προγόνους που μείωσαν το πεδίο του var
        
        for value in order_domain_values(var, assignment, csp):
            if csp.nconflicts(var, value, assignment) == 0:
                csp.assign(var, value, assignment)
                removals = csp.suppose(var, value)
                
                consistent, dwo_var = check_forward(var, assignment, removals)
                
                if consistent:
                    result, conflict_from_below = backtrack(assignment)
                    if result is not None:
                        return result, None
                    
                    # Backtrack από χαμηλά
                    if conflict_from_below is not None:
                        if var in conflict_from_below:
                            # Είμαστε στο conflict set, άρα εμείς (ή κάποιος πριν) φταίμε.
                            # Προσπαθούμε άλλη τιμή.
                            # Ενημερώνουμε το δικό μας conflict set με τα υπόλοιπα του conflict_from_below
                            conf_set[var].update(conflict_from_below)
                            conf_set[var].discard(var)
                        else:
                            # Δεν φταίμε εμείς, πρέπει να πάμε πιο πίσω
                            csp.restore(removals)
                            csp.unassign(var, assignment)
                            return None, conflict_from_below
                else:
                    # DWO συνέβη στο dwo_var
                    # Ενημερώνουμε το conflict set του var με αυτό του dwo_var
                    if hasattr(csp, 'constraint_weights'):
                         edge = tuple(sorted((var, dwo_var)))
                         csp.constraint_weights[edge] += 1
                         
                    conf_set[var].update(conf_set[dwo_var])
                    # Και προσθέτουμε και τον dwo_var; Όχι, είναι μελλοντικός.
                    # Το conf_set[dwo_var] έχει τους παλιούς που το περιόρισαν.
                
                csp.restore(removals)
                csp.unassign(var, assignment)
        
        # Αν εξαντλήσαμε τις τιμές, επιστρέφουμε πίσω (backtrack)
        # Επιστρέφουμε το conflict set μας για να ξέρει ο γονιός πού να πάει
        return None, conf_set[var]

    result, _ = backtrack({})
    return result
