from itertools import product
from collections import defaultdict
import sympy as sp

class ProbabilityCalculator:
    def __init__(self, variables, domain):
        """
        Initialize the probability calculator with:
        - variables: List of variables in the program
        - domain: Dictionary mapping each variable to its discrete uniform range
        """
        self.variables = variables
        self.domain = domain
        self.total_cases = list(product(*[domain[var] for var in variables]))

    def compute_probability(self, condition):
        """
        Compute the probability of a condition being True.
        If condition is dependent on a previous condition, use conditional probability.
        """
        valid_cases = [case for case in self.total_cases if self.evaluate_condition(condition, case)]
        return len(valid_cases) / len(self.total_cases)

    def compute_conditional_probability(self, condition, given_condition):
        """
        Compute P(condition | given_condition)
        """
        given_cases = [case for case in self.total_cases if self.evaluate_condition(given_condition, case)]
        valid_cases = [case for case in given_cases if self.evaluate_condition(condition, case)]
        
        if not given_cases:  # Avoid division by zero
            return 0
        return len(valid_cases) / len(given_cases)

    def evaluate_condition(self, condition, case):
        """
        Evaluate a boolean condition against a given case.
        Example:
        condition = 'x > 1', case = (x=2, y=3)
        """
        local_env = {var: val for var, val in zip(self.variables, case)}
        return eval(condition, {}, local_env)

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

            path_probabilities[tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome) for cond, outcome in path)] = probability


        return path_probabilities



variables = ['x']
domain = {
    'x' : [1, 2, 3]
}
# Define the problem setup
"""variables = ['x', 'y','z','choice' ,
    'door_switch' ,
    'car_door' , 'host_door' , 'px','py']
domain = {
    'x': [0,1, 2, 3,4,5,6,7,8,9,10],
    'y': [0,1, 2, 3,4,5,6,7,8,9,10],
    'z': [1, 2, 3] , 
    'choice' : [1,2,3],
    'door_switch' : [1],
    'car_door' : [1,2,3] ,
    'host_door' : [1,2,3] , 
    'px': list(range(0,101)),
    'py': list(range(0,101))
}

variables =['px','py']
domain = {
    'px' : list(range(0,1001)),
    'py' : list (range(0,1001))
}
"""


# extracted_paths7 = [
#     [('x > 1', 'True'), ('x > 2', 'True'), ('Statements', ['return 1'])],
# [('x > 1', 'True'), ('x > 2', 'False'), ('Statements', ['return 0'])],
# [('x > 1', 'False'), ('Statements', ['pass'])],
# [('x > 3', 'True'), ('Statements', ['return 1'])],
# [('x > 3', 'False'), ('Statements', ['pass'])]
# ]

# Define extracted paths
extracted_paths = [
    [('x > 1', 'True'), ('x > y', 'True'), ('Statements', ['return True'])],[('x > 1', 'False'), ('Statements', ['return False'])],
[('x > 1', 'True'), ('x > y', 'False'), ('Statements', ['return False'])] 
 
]

#another example 
extracted_paths3 = [
    [('x > 1', 'True'), ('y > x', 'True'), ('z > 1', 'True'), ('Statements', ['return 1'])]
]
#example 3 
extracted_paths2 = [
    [('x > 1', 'True'), ('x > y', 'True'), ('Statements', ['return 1'])],
[('x > 1', 'True'), ('x > y', 'False'), ('Statements', ['return 0'])],
[('x > 1', 'False'), ('x == 0', 'True'), ('Statements', ['return 0'])],
[('x > 1', 'False'), ('x == 0', 'False'), ('Statements', ['return 0'])]
]


extracted_paths4 = [
    [('x > 1', 'True'), ('x > 2', 'False'), ('Statements', ['return 1'])]
]

extracted_paths5 = [
[('choice == car_door', 'True'), ('Statements', ['return not door_switch'])],
[('choice == car_door', 'False'), ('Statements', ['pass'])],
[('choice != 1 and car_door != 1', 'True'), ('Statements', ['host_door = 1'])],
[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('Statements', ['host_door = 2'])],
[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('Statements', ['host_door = 3'])],
[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'True'), ('Statements', ['choice = 3'])],
[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'False'), ('Statements', ['choice = 2'])],
[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'True'), ('Statements', ['choice = 3'])],
[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'False'), ('Statements', ['choice = 1'])],
[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'True'), ('Statements', ['choice = 2'])],
[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'False'), ('Statements', ['choice = 1'])],
[('door_switch', 'False'), ('Statements', ['pass'])],
[('choice == car_door', 'True'), ('Statements', ['return 1'])],
[('choice == car_door', 'False'), ('Statements', ['pass'])]
]


extracted_paths6 = [

    [('choice == car_door', 'True'), ('Statements', ['return not door_switch'])],
[('choice == car_door', 'False'), ('Statements', ['pass'])],
[('choice != 1 and car_door != 1', 'True'), ('Statements', ['host_door = 1'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('Statements', ['host_door = 2'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('Statements', ['host_door = 3'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'False'), ('Statements', ['choice = 2']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'False'), ('Statements', ['choice = 2']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'True'), ('Statements', ['choice = 2']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'True'), ('Statements', ['choice = 2']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'False'), ('Statements', ['pass'])]
]



extracted_paths8 = [
    [('px**2 + py**2 <= 1000000', 'True'), ('Statements', ['return 1'])],
#[('px**2 + py**2 <= 100*100', 'False'), ('Statements', ['return 0'])]
]

extracted_paths9 = [

    [('A * (B * r) == C * r ', 'True'), ('Statements', ['return True'])],
[('A * (B * r) == C * r', 'False'), ('Statements', ['return False'])]
]



extracted_paths41 = [
    [('x < 1', 'True'), ('Statements', ['return 1'])]
]
# Create ProbabilityCalculator instance
calculator = ProbabilityCalculator(variables, domain)

# Compute probabilities
path_probabilities = calculator.calculate_path_probabilities(extracted_paths41)

# Print results
for path, probability in path_probabilities.items():
    print(f"Path: {path}")
    print(f"Probability: {probability:.6f}\n")
