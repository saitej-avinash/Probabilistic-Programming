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
        Compute probabilities for all extracted paths,
        accounting for variable updates in 'Statements'.
        """
        path_probabilities = {}
        
        # Debug function to better understand the filtering process
        def debug_cases(cases, condition_str):
            print(f"Condition: {condition_str}")
            print(f"Remaining cases: {len(cases)}")
            if len(cases) < 10:  # Only print if reasonable number of cases
                print(f"Cases: {cases}")
            print("---")

        for path in paths:
            # Print the current path for debugging
            print(f"\nEvaluating path: {path}")
            
            probability = 1.0
            current_cases = self.total_cases.copy()  # Start with all cases
            
            for i, (condition, outcome) in enumerate(path):
                if condition == 'Statements':
                    # Skip statements for probability calculation
                    continue
                
                # Build the condition string based on the outcome
                condition_str = condition if outcome == 'True' else f"not ({condition})"
                
                # Count cases before applying this condition
                before_count = len(current_cases)
                
                # Filter cases that satisfy the current condition
                if outcome == 'True':
                    filtered_cases = [case for case in current_cases if self.evaluate_condition(condition, case)]
                else:
                    filtered_cases = [case for case in current_cases if not self.evaluate_condition(condition, case)]
                
                # Count cases after filtering
                after_count = len(filtered_cases)
                
                # Calculate branch probability
                branch_probability = after_count / before_count if before_count > 0 else 0
                
                # Debug information
                print(f"Step {i+1}: {condition_str}")
                print(f"  Before: {before_count} cases")
                print(f"  After: {after_count} cases")
                print(f"  Branch probability: {branch_probability:.6f}")
                
                # Update the total path probability
                probability *= branch_probability
                
                # Update current_cases for the next condition
                current_cases = filtered_cases
                
                # If we've eliminated all cases, we can stop
                if not current_cases:
                    probability = 0
                    break
            
            # Store the final probability for this path
            path_key = tuple((cond, tuple(out) if isinstance(out, list) else out) for cond, out in path)
            path_probabilities[path_key] = probability
            print(f"Final path probability: {probability:.6f}")
        
        return path_probabilities


# Testing the fixed implementation with the Monty Hall problem
if __name__ == "__main__":
    # Define the problem setup
    variables = ['choice', 'car_door']
    domain = {
        'choice': [1, 2, 3],
        'car_door': [1, 2, 3]
    }

    # Create a simplified test case focusing on the problematic path
    test_path = [
        ('choice != 1 and car_door != 1', 'False'),
        ('choice != 2 and car_door != 2', 'False'),
        ('choice != 3 and car_door != 3', 'True'),
        ('choice == 1', 'True'),
        ('car_door == 2', 'False'),
        ('car_door == 1', 'True'),
        ('Statements', ['return 1'])
    ]
    
    # Create calculator and compute probabilities
    calculator = ProbabilityCalculator(variables, domain)
    
    # Debug: show all possible cases
    print("All possible cases:")
    for i, case in enumerate(calculator.total_cases):
        print(f"Case {i+1}: {dict(zip(variables, case))}")
    
    # Compute probabilities for the test path
    path_probabilities = calculator.calculate_path_probabilities([test_path])
    
    # Print the result
    for path, probability in path_probabilities.items():
        print(f"\nPath probability: {probability:.6f}")
        
    # Now run the full set of paths
    extracted_paths = [
        [('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'True'), ('car_door == 3', 'True'), ('Statements', ['return 1'])],
        [('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'True'), ('car_door == 3', 'False'), ('car_door == 2', 'True'), ('Statements', ['return 1'])],
        [('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'True'), ('car_door == 3', 'False'), ('car_door == 2', 'False'), ('Statements', ['pass'])],
        [('choice != 1 and car_door != 1', 'True'), ('choice == 2', 'False'), ('Statements', ['pass'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'True'), ('car_door == 3', 'True'), ('Statements', ['return 1'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'True'), ('car_door == 3', 'False'), ('car_door == 1', 'True'), ('Statements', ['return 1'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'True'), ('car_door == 3', 'False'), ('car_door == 1', 'False'), ('Statements', ['pass'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('choice == 1', 'False'), ('Statements', ['pass'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'True'), ('car_door == 2', 'True'), ('Statements', ['return 1'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'True'), ('car_door == 2', 'False'), ('car_door == 1', 'True'), ('Statements', ['return 1'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'True'), ('car_door == 2', 'False'), ('car_door == 1', 'False'), ('Statements', ['pass'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'True'), ('choice == 1', 'False'), ('Statements', ['pass'])],
        [('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('choice != 3 and car_door != 3', 'False'), ('Statements', ['pass'])]
    ]
    
    print("\n\n===== Full Path Analysis =====\n")
    full_probabilities = calculator.calculate_path_probabilities(extracted_paths)
    
    print("\n===== Summary of All Path Probabilities =====")
    for path, probability in full_probabilities.items():
        simplified_path = [(c, o) for c, o in path if c != 'Statements']
        print(f"Path: {simplified_path}")
        print(f"Probability: {probability:.6f}\n")