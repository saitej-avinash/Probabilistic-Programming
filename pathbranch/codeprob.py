from itertools import product

def monty_hall_function(choice, car_door):
    """Implementation of the given code logic"""
    if choice != 1 and car_door != 1:
        if choice == 2:
            if car_door == 3:
                return 1
        else:
            if car_door == 2:
                return 1
    elif choice != 2 and car_door != 2:
        if choice == 1:
            if car_door == 3:
                return 1
        else:
            if car_door == 1:
                return 1
    elif choice != 3 and car_door != 3:
        if choice == 1:
            if car_door == 2:
                return 1
        else:
            if car_door == 1:
                return 1
    
    # If no condition is met, implicitly return None (which is falsy)
    return 0

# Domain of variables
variables = ['choice', 'car_door']
domain = {
    'choice': [1, 2, 3],
    'car_door': [1, 2, 3]
}

# Generate all possible combinations
all_combinations = list(product(*[domain[var] for var in variables]))

# Test each combination
results = []
for combo in all_combinations:
    choice, car_door = combo
    result = monty_hall_function(choice, car_door)
    results.append((combo, result))
    print(f"choice={choice}, car_door={car_door} => {'Returns 1' if result == 1 else 'No return (0)'}")

# Calculate probability
successful_outcomes = sum(1 for _, result in results if result == 1)
total_outcomes = len(all_combinations)
probability = successful_outcomes / total_outcomes

print(f"\nTotal combinations: {total_outcomes}")
print(f"Combinations that return 1: {successful_outcomes}")
print(f"Probability: {successful_outcomes}/{total_outcomes} = {probability:.6f} or {probability:.2%}")

# Show all combinations that return 1
print("\nCombinations that return 1:")
for combo, result in results:
    if result == 1:
        choice, car_door = combo
        print(f"(choice={choice}, car_door={car_door})")