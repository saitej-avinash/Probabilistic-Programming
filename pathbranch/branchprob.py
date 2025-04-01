from itertools import product

class BranchProbabilityCalculator:
    def __init__(self, variables, domain):
        """
        Initialize the probability calculator with:
        - variables: List of variables in the program
        - domain: Dictionary mapping each variable to its discrete uniform range
        """
        self.variables = variables
        self.domain = domain
        self.total_cases = list(product(*[domain[var] for var in variables]))

    def make_hashable(self, item):
        """ Recursively convert lists to tuples to ensure hashability. """
        if isinstance(item, list):
            return tuple(self.make_hashable(subitem) for subitem in item)
        elif isinstance(item, tuple):
            return tuple(self.make_hashable(subitem) for subitem in item)
        elif isinstance(item, dict):
            return tuple((key, self.make_hashable(value)) for key, value in sorted(item.items()))  # Convert dict to tuple
        return item  # Keep other data types unchanged

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

    def calculate_branch_probabilities(self, paths):
        """
        Compute probabilities for all branches within each path.
        """
        all_path_branch_probabilities = {}

        for path in paths:
            branch_probabilities = []  # Ensure this remains a list
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
                
                # Store branch probability as a tuple
                branch_probabilities.append((condition, outcome, branch_probability))

            # ✅ Fix: Recursively convert lists, tuples, and dicts inside path to tuples
            hashable_path = tuple(self.make_hashable(item) for item in path)

            # Ensure branch_probabilities remains a list
            all_path_branch_probabilities[hashable_path] = list(branch_probabilities)

        return all_path_branch_probabilities


# Define the problem setup
variables = ['x', 'y','z','choice' ,
    'door_switch' ,
    'car_door' , 'host_door']
domain = {
    'x': [1, 2, 3,4,5,6], # dice problem
    'y': [1, 2, 3],
    'z': [1, 2, 3] , 
    'choice' : [1,2,3],
    'door_switch' : [1],
    'car_door' : [1,2,3] ,
    'host_door' : [1,2,3]
}

# Define extracted paths
extracted_paths = [
    [('x > 1', 'True'), ('x < y', 'True'), ('Statements', ['return True'])],
    [('x > 1', 'True'), ('x < y', 'False'), ('Statements', ['return False'])],
    [('x > 1', 'False'), ('Statements', ['return False'])]
]

extracted_paths2 =[
    [('x > 1', 'True'), ('x > 2', 'True'), ('Statements', ['return 1'])],
[('x > 1', 'True'), ('x > 2', 'False'), ('Statements', ['return 0'])],
[('x > 1', 'False'), ('Statements', ['pass'])],
[('x > 3', 'True'), ('Statements', ['return 1'])],
[('x > 3', 'False'), ('Statements', ['return 2'])]
]

extracted_paths1 = [
    [('x > 1', 'True'), ('x > 2', 'True'), ('Statements', ['return 1'])]
]

extracted_paths7 = [[('x > 2', 'True'), ('Statements', ['y = 1'])],
[('x > 2', 'False'), ('Statements', ['y = 0'])]]


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
[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'False'), ('Statements', ['choice = 10'])],
[('door_switch', 'False'), ('Statements', ['pass'])],
[('choice == car_door', 'True'), ('Statements', ['return 1'])],
[('choice == car_door', 'False'), ('Statements', ['pass'])]
]


# Create BranchProbabilityCalculator instance
calculator = BranchProbabilityCalculator(variables, domain)

# Compute branch probabilities
path_branch_probabilities = calculator.calculate_branch_probabilities(extracted_paths7)

# Print results
for path, branch_probs in path_branch_probabilities.items():
    print(f"Path: {path}")
    for condition, outcome, prob in branch_probs:
        print(f"  Branch: {condition} = {outcome}, Probability: {prob:.6f}")
    print()
