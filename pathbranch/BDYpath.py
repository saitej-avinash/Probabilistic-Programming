import math

def birthday_shared_prob(k, days=365):
    if k > days:
        return 1.0
    prob_no_shared = 1.0
    for i in range(k):
        prob_no_shared *= (days - i) / days
    return 1.0 - prob_no_shared

def make_birthday_paths(k, days=365):
    """
    Return two paths in the same structure as your other examples,
    with 'return 1' meaning shared-birthday found, 'return 0' otherwise.
    Probabilities are computed analytically (no enumeration).
    """
    p_shared = birthday_shared_prob(k, days)
    p_no_shared = 1.0 - p_shared

    extracted_birthday_paths = [
        [('BIRTHDAY_SHARED(k={},days={})'.format(k, days), 'True'),
         ('Statements', ['return 1'])],

        [('BIRTHDAY_SHARED(k={},days={})'.format(k, days), 'False'),
         ('Statements', ['return 0'])]
    ]

    # Put them in the same dict format your printer expects
    path_probabilities = {}
    key_true = tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome)
                     for cond, outcome in extracted_birthday_paths[0])
    key_false = tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome)
                      for cond, outcome in extracted_birthday_paths[1])

    path_probabilities[key_true] = p_shared
    path_probabilities[key_false] = p_no_shared

    return extracted_birthday_paths, path_probabilities


# ----- Example usage -----
k = 20
paths, probs = make_birthday_paths(k, days=365)

for path, p in probs.items():
    print("Path:", path)
    print(f"Probability: {p:.6f}\n")
