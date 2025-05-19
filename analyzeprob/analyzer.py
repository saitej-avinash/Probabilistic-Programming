import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import defaultdict
from conditionals.condition_tree_builder import ConditionTreeBuilder
from conditionals.path_extractor import extract_paths
from pathbranch.probability_calculator import ProbabilityCalculator

def analyze_return_probabilities(code, variables, domain):
    """
    Analyze return value probabilities of a Python function using symbolic path analysis.
    
    Args:
        code (str): The Python function source code as a string.
        variables (list): List of symbolic variables used in conditions.
        domain (dict): Dictionary mapping each variable to its domain (possible values).
    
    Returns:
        result_distribution (dict): Probabilities for each return value.
        path_probs (dict): Probabilities for each symbolic execution path.
    """
    # Step 1: Parse AST and build condition tree
    builder = ConditionTreeBuilder()
    condition_tree = builder.build_tree(code)

    # Step 2: Extract all true/false execution paths from condition tree
    paths = extract_paths(condition_tree)

    # Step 3: Compute symbolic probabilities for all paths
    calc = ProbabilityCalculator(variables, domain)
    path_probs = calc.calculate_path_probabilities(paths)

    # Step 4: Evaluate return values (including symbolic expressions like "not door_switch")
    result_distribution = defaultdict(float)
    for path, prob in path_probs.items():
        found_return = False
        for cond, stmt in path:
            if cond == "Statements":
                for s in stmt:
                    if s.strip().startswith("return"):
                        return_expr = s.strip().replace("return", "").strip()
                        found_return = True
                        try:
                            true_count = 0
                            for case in calc.total_cases:
                                local_env = dict(zip(variables, case))
                                result = eval(return_expr, {}, local_env)
                                if result:
                                    true_count += 1
                            ratio = true_count / len(calc.total_cases)
                            result_distribution['1'] += ratio * prob
                            result_distribution['0'] += (1 - ratio) * prob
                        except:
                            result_distribution[return_expr] += prob
        if not found_return:
            # If no return statement was executed in this path, assume default return 0
            result_distribution['0'] += prob

    return result_distribution, path_probs
