
"""Parser for RLFAP instance files (variables, domains, and constraints)."""

def parse_domains(filepath):
    """
    Διαβάζει το αρχείο domains (π.χ. dom11.txt).
    Επιστρέφει ένα λεξικό {domain_id: [values]}.
    """
    domains = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
        # Η πρώτη γραμμή είναι το πλήθος, την αγνοούμε
        for line in lines[1:]:
            parts = list(map(int, line.split()))
            dom_id = parts[0]
            # Το parts[1] είναι το πλήθος των τιμών, τα υπόλοιπα είναι οι τιμές
            values = parts[2:]
            domains[dom_id] = values
    return domains

def parse_variables(filepath, domains_dict):
    """
    Διαβάζει το αρχείο variables (π.χ. var11.txt).
    Χρειάζεται το λεξικό των domains για να αντιστοιχίσει τιμές.
    Επιστρέφει {var_id: [domain_values]}.
    """
    variables = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            parts = list(map(int, line.split()))
            var_id = parts[0]
            dom_id = parts[1]
            # Αντιστοιχίζουμε το domain id με τις πραγματικές τιμές
            if dom_id in domains_dict:
                variables[var_id] = domains_dict[dom_id]
            else:
                print(f"Warning: Domain {dom_id} not found for variable {var_id}")
    return variables

def parse_constraints(filepath):
    """
    Διαβάζει το αρχείο constraints (π.χ. ctr11.txt).
    Επιστρέφει μια λίστα από tuples (var1, var2, operator, k).
    """
    constraints = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            parts = line.split()
            var1 = int(parts[0])
            var2 = int(parts[1])
            operator = parts[2]
            k = int(parts[3])
            constraints.append((var1, var2, operator, k))
    return constraints
