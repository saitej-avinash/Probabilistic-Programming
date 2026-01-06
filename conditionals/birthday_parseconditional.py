from itertools import product

def extract_birthday_paths(k=4, days=7):
    """Extract birthday paradox paths in parseconditional format"""
    
    paths = []
    
    # Generate all possible sequences
    for sequence in product(range(days), repeat=k):
        seen_values = set()
        path_conditions = []
        collision_found = False
        
        # Process each iteration
        for i, b_value in enumerate(sequence):
            # Add sampling condition
            path_conditions.append((f'b{i} == {b_value}', 'True'))
            
            # Check collision
            if b_value in seen_values:
                path_conditions.append((f'seen[{b_value}] == 1', 'True'))
                path_conditions.append(('Statements', ['return 1']))
                collision_found = True
                break
            else:
                path_conditions.append((f'seen[{b_value}] == 0', 'True'))
                seen_values.add(b_value)
        
        # If no collision after k iterations
        if not collision_found:
            path_conditions.append(('Statements', ['return 0']))
        
        paths.append(path_conditions)
    
    return paths

# Generate and print paths
if __name__ == "__main__":
    paths = extract_birthday_paths(k=4, days=7)
    
    print("\nExtracted Paths:")
    for path in paths:
        print(path)
