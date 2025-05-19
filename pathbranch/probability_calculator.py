from itertools import product

class ProbabilityCalculator:
    def __init__(self, variables, domain):
        self.variables = variables
        self.domain = domain
        self.total_cases = list(product(*[domain[var] for var in variables]))

    def compute_probability(self, condition):
        valid_cases = [case for case in self.total_cases if self.evaluate_condition(condition, case)]
        return len(valid_cases) / len(self.total_cases)

    def compute_conditional_probability(self, condition, given_condition):
        given_cases = [case for case in self.total_cases if self.evaluate_condition(given_condition, case)]
        valid_cases = [case for case in given_cases if self.evaluate_condition(condition, case)]
        if not given_cases:
            return 0
        return len(valid_cases) / len(given_cases)

    def evaluate_condition(self, condition, case):
        local_env = {var: val for var, val in zip(self.variables, case)}
        try:
            return eval(condition, {}, local_env)
        except Exception:
            return False

    def calculate_path_probabilities(self, paths):
        path_probabilities = {}
        for path in paths:
            probability = 1
            previous_conditions = []

            for condition, outcome in path[:-1]:  # Ignore the return/statement
                condition_str = condition if outcome == 'True' else f"not ({condition})"

                if not previous_conditions:
                    branch_prob = self.compute_probability(condition_str)
                else:
                    given_condition_str = " and ".join(previous_conditions)
                    branch_prob = self.compute_conditional_probability(condition_str, given_condition_str)

                probability *= branch_prob
                previous_conditions.append(condition_str)

            formatted_path = tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome) for cond, outcome in path)
            path_probabilities[formatted_path] = probability

        return path_probabilities
