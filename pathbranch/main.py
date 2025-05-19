from probability_calculator import ProbabilityCalculator
from extracted_paths_data import variables, domain, extracted_paths6
calculator = ProbabilityCalculator(variables, domain)
path_probabilities = calculator.calculate_path_probabilities(extracted_paths6)

for path, prob in path_probabilities.items():
    print(f"Path: {path}")
    print(f"Probability: {prob:.6f}\n")
