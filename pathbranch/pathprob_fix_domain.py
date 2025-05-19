from itertools import product
from collections import defaultdict


class ProbabilityCalculator:
    def __init__(self, variables, domain):
        """
        Initialize the probability calculator with:
        - variables: List of variables in the program
        - domain: Dictionary mapping each variable to its discrete uniform range
        """
        self.variables = variables
        self.domain = domain

    def evaluate_condition(self, condition, case):
        """
        Evaluate a boolean condition against a given case.
        Example:
        condition = 'x > 1', case = (x=2, y=3)
        """
        local_env = {var: val for var, val in zip(self.variables, case)}
        try:
            return eval(condition, {}, local_env)
        except:
            return False

    def count_valid_cases(self, condition, condition_filter=None):
        """
        Count how many cases satisfy the given condition (and optional filter).
        Uses a generator to avoid large memory usage.
        """
        count = 0
        total = 0
        for case in product(*[self.domain[var] for var in self.variables]):
            if condition_filter and not self.evaluate_condition(condition_filter, case):
                continue
            total += 1
            if self.evaluate_condition(condition, case):
                count += 1
        return count, total

    def compute_probability(self, condition):
        """
        Compute the probability of a condition being True.
        """
        count, total = self.count_valid_cases(condition)
        return count / total if total else 0

    def compute_conditional_probability(self, condition, given_condition):
        """
        Compute P(condition | given_condition)
        """
        count, total = self.count_valid_cases(condition, condition_filter=given_condition)
        return count / total if total else 0

    def calculate_path_probabilities(self, paths):
        """
        Compute probabilities for all extracted paths.
        """
        path_probabilities = {}
        for path in paths:
            probability = 1
            previous_conditions = []

            for condition, outcome in path[:-1]:  # Ignore the return statement
                if outcome == 'True':
                    condition_str = condition
                else:
                    condition_str = f"not ({condition})"

                if not previous_conditions:
                    branch_probability = self.compute_probability(condition_str)
                else:
                    given_condition_str = " and ".join(previous_conditions)
                    branch_probability = self.compute_conditional_probability(condition_str, given_condition_str)

                probability *= branch_probability
                previous_conditions.append(condition_str)

            key = tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome) for cond, outcome in path)
            path_probabilities[key] = probability

        return path_probabilities


# --------------------- TEST SETUP ---------------------

#variables = ['x', 'y','z','choice' ,'door_switch' ,'car_door' , 'host_door' , 'px','py']

variables = ['choice'  ,'car_door' ]

domain = {
    #'x': [0,1, 2, 3,4,5,6,7,8,9,10],
   # 'y': [0,1, 2, 3,4,5,6,7,8,9,10],
   # 'z': [1, 2, 3] , 
    'choice' : [1,2,3],
   # 'door_switch' : [1],
    'car_door' : [1,2,3] 
   # 'host_door' : [1,2,3] , 
    #'px': list(range(0,101)),
    #'py': list(range(0,101))
}

# Sample path to test



extracted_paths42 = [

    [('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'True'), ('car_door == 3', 'True'), ('Statements', ['return 1'])]
,[('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'True'), ('car_door == 3', 'False'), ('Statements', ['pass'])]
,[('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'False'), ('car_door == 2', 'True'), ('Statements', ['return 1'])]
,[('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'False'), ('car_door == 2', 'False'), ('Statements', ['pass'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'True'), ('car_door == 3', 'True'), ('Statements', ['return 1'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'True'), ('car_door == 3', 'False'), ('Statements', ['pass'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'False'), ('car_door == 1', 'True'), ('Statements', ['return 1'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'False'), ('car_door == 1', 'False'), ('Statements', ['pass'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'True'), ('car_door == 2', 'True'), ('Statements', ['return 1'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'True'), ('car_door == 2', 'False'), ('Statements', ['pass'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'False'), ('car_door == 1', 'True'), ('Statements', ['return 1'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'False'), ('car_door == 1', 'False'), ('Statements', ['pass'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'False'), ('Statements', ['pass'])]
]

# Create calculator instance
calculator = ProbabilityCalculator(variables, domain)

# Compute probabilities
path_probabilities = calculator.calculate_path_probabilities(extracted_paths42)

# Print results
for path, probability in path_probabilities.items():
    print(f"Path: {path}")
    print(f"Probability: {probability:.6f}\n")
 