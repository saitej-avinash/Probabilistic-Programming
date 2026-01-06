import ast
from itertools import product
from collections import defaultdict

class ProbabilityCalculator:
    def __init__(self, variables, domain):
        self.variables = variables
        self.domain = domain

    def evaluate_condition(self, condition, case):
        local_env = {var: val for var, val in zip(self.variables, case)}
        try:
            return eval(condition, {}, local_env)
        except:
            return False

    def count_valid_cases(self, condition, condition_filter=None):
        count = 0
        total = 0
        
        for case in product(*[self.domain[var] for var in self.variables]):
            if condition_filter:
                if not self.evaluate_condition(condition_filter, case):
                    continue
            
            total += 1 
            
            if self.evaluate_condition(condition, case):
                count += 1
                
        return count, total

    def compute_probability(self, condition):
        total_domain_size = 1
        for var in self.variables:
            total_domain_size *= len(self.domain[var])
        
        count, _ = self.count_valid_cases(condition)

        return count / total_domain_size if total_domain_size else 0

    def compute_conditional_probability(self, condition, given_condition):
        count, total = self.count_valid_cases(condition, condition_filter=given_condition)
        return count / total if total else 0

    def calculate_path_probabilities(self, paths):
        path_probabilities = {}
        for path in paths:
            probability = 1.0
            previous_conditions = []

            for segment in path:
                if segment[0] == 'Statements':
                    # FIX: Continue to skip statement segments but maintain chain integrity
                    continue 

                condition, outcome = segment
                
                if outcome == 'True':
                    condition_str = condition
                elif outcome == 'False':
                    # Use parentheses for correct negation evaluation
                    condition_str = f"not ({condition})"
                else:
                    continue

                if not previous_conditions:
                    # Non-conditional probability P(C1)
                    branch_probability = self.compute_probability(condition_str)
                else:
                    # Conditional probability P(C_n | C_1 AND ... AND C_{n-1})
                    given_condition_str = " and ".join(previous_conditions)
                    branch_probability = self.compute_conditional_probability(condition_str, given_condition_str)

                # Chain the probabilities
                probability *= branch_probability
                previous_conditions.append(condition_str)

            # Use the full path tuple as the key
            key = tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome) for cond, outcome in path)
            path_probabilities[key] = probability

        return path_probabilities
    
example_7 = [
    [('x > 1', 'True'), ('x > 2', 'True'), ('Statements', ['return 1'])]
,[('x > 1', 'True'), ('x > 2', 'False'), ('Statements', ['return 0'])]
,[('x > 1', 'False'), ('Statements', ['pass']), ('x > 3', 'True'), ('Statements', ['return 0'])]
,[('x > 1', 'False'), ('Statements', ['pass']), ('x > 3', 'False'), ('Statements', ['pass'])]
]

extracted_pipaths = [
    [('px**2 + py**2 <= 315*315', 'True'), ('Statements', ['return 1'])],
    [('px**2 + py**2 <= 315*315', 'False'), ('Statements', ['return 0'])]
]


# 2. Define Domain (x in [0, 10] inclusive)
variables = ['x']
domain = {'x': range(0, 11)} # 0, 1, 2, ..., 10 (11 values total)

pivaribles = ['px', 'py']
domain_pipaths = {
    'px': list(range(0, 315)),
    'py': list(range(0, 315))
}


picalculator = ProbabilityCalculator(pivaribles, domain_pipaths)
pipath_probabilities = picalculator.calculate_path_probabilities(extracted_pipaths)     
for path, probability in pipath_probabilities.items():
    print(f"Path: {path}")
    print(f"Probability: {probability:.6f}\n")
    

# Create calculator instance
calculator = ProbabilityCalculator(variables, domain)

# Compute probabilities
path_probabilities = calculator.calculate_path_probabilities(example_7)

# Print results
for path, probability in path_probabilities.items():
    print(f"Path: {path}")
    print(f"Probability: {probability:.6f}\n")
 