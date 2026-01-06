import math

def birthday_probability(k):
    # Total days in a year (ignoring leap years)
    days_in_year = 7
    
    # If the group size is too large, the probability of shared birthday is 100%
    if k > days_in_year:
        return 1.0
    
    # Probability that no one shares a birthday
    probability_no_shared = 1.0
    for i in range(k):
        probability_no_shared *= (days_in_year - i) / days_in_year
    
    # Probability that at least two people share a birthday
    probability_shared = 1 - probability_no_shared
    
    return probability_shared

# Example usage
k = 4
print(f"Probability that at least two people share a birthday in a group of {k} people: {birthday_probability(k):.4f}")
