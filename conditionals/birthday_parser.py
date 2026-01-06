import ast
from itertools import product

class ConditionNode:
    def __init__(self, condition=None):
        self.condition = condition
        self.true_statements = []
        self.false_statements = []
        self.true_branch = None
        self.false_branch = None
        self.next_condition = None

    def __repr__(self):
        return f"ConditionNode(condition={self.condition})"

class BirthdayPathExtractor:
    def __init__(self, k=4, days=7):
        self.k = k
        self.days = days
        self.paths = []
    
    def extract_birthday_paths(self):
        """Extract all possible paths for birthday paradox"""
        
        # Generate all possible sequences of k random samples
        for sequence in product(range(self.days), repeat=self.k):
            path_conditions = []
            collision_found = False
            collision_iteration = -1
            
            # Check each iteration for collisions
            seen_values = set()
            for i, b_value in enumerate(sequence):
                # Add condition for this sample
                path_conditions.append(f"b{i} == {b_value}")
                
                # Check if collision occurs
                if b_value in seen_values:
                    collision_found = True
                    collision_iteration = i
                    path_conditions.append(f"seen[{b_value}] == 1")
                    break
                else:
                    path_conditions.append(f"seen[{b_value}] == 0")
                    seen_values.add(b_value)
            
            # Determine outcome
            if collision_found:
                outcome = "return 1"
                path_type = f"collision_at_iteration_{collision_iteration}"
            else:
                outcome = "return 0"
                path_type = "no_collision"
            
            # Create path
            path = {
                'conditions': path_conditions,
                'outcome': outcome,
                'type': path_type,
                'sequence': sequence,
                'collision_at': collision_iteration if collision_found else None
            }
            
            self.paths.append(path)
        
        return self.paths
    
    def get_unique_path_types(self):
        """Group paths by their logical structure"""
        path_groups = {}
        
        for path in self.paths:
            path_type = path['type']
            if path_type not in path_groups:
                path_groups[path_type] = []
            path_groups[path_type].append(path)
        
        return path_groups
    
    def compute_path_probabilities(self):
        """Compute probability for each path type"""
        total_sequences = self.days ** self.k
        path_groups = self.get_unique_path_types()
        
        probabilities = {}
        for path_type, paths in path_groups.items():
            count = len(paths)
            probability = count / total_sequences
            probabilities[path_type] = {
                'count': count,
                'probability': probability,
                'paths': len(paths)
            }
        
        return probabilities

class LoopConditionBuilder(ast.NodeVisitor):
    def __init__(self):
        self.root = None
        self.loop_info = {}
    
    def visit_While(self, node):
        """Handle while loops by extracting loop bounds and body"""
        condition = ast.unparse(node.test)
        
        # Extract loop information
        self.loop_info = {
            'condition': condition,
            'body': [ast.unparse(stmt) for stmt in node.body],
            'type': 'while_loop'
        }
        
        # For birthday paradox, we know it's bounded by k
        if 'i < k' in condition:
            self.loop_info['bounded'] = True
            self.loop_info['max_iterations'] = 'k'
    
    def visit_If(self, node):
        """Handle if statements within loops"""
        condition = ast.unparse(node.test)
        true_body = [ast.unparse(stmt) for stmt in node.body]
        false_body = [ast.unparse(stmt) for stmt in node.orelse] if node.orelse else []
        
        return {
            'condition': condition,
            'true_body': true_body,
            'false_body': false_body
        }

def analyze_birthday_paradox():
    """Main function to analyze birthday paradox"""
    
    example_birthday = """
days = 7
k = 4
seen = [0] * days
i = 0

while i < k:
    b = sample_uniform(0, days - 1)
    if seen[b] == 1:
        return 1
    else:
        seen[b] = 1
    i = i + 1
else:
    return 0
"""
    
    print("=== Birthday Paradox Path Analysis ===\n")
    
    # Parse the AST to understand structure
    tree = ast.parse(example_birthday)
    builder = LoopConditionBuilder()
    builder.visit(tree)
    
    print("Loop Structure:")
    print(f"Condition: {builder.loop_info.get('condition', 'None')}")
    print(f"Body: {builder.loop_info.get('body', [])}")
    print()
    
    # Extract all possible paths
    extractor = BirthdayPathExtractor(k=4, days=7)
    paths = extractor.extract_birthday_paths()
    
    print(f"Total possible sequences: {7**4} = {len(paths)}")
    print()
    
    # Group by path types
    path_groups = extractor.get_unique_path_types()
    
    print("Path Types:")
    for path_type, group_paths in path_groups.items():
        print(f"  {path_type}: {len(group_paths)} paths")
    print()
    
    # Compute probabilities
    probabilities = extractor.compute_path_probabilities()
    
    print("Path Probabilities:")
    total_prob = 0
    for path_type, prob_info in probabilities.items():
        print(f"  {path_type}:")
        print(f"    Count: {prob_info['count']}")
        print(f"    Probability: {prob_info['probability']:.6f}")
        total_prob += prob_info['probability']
    
    print(f"\nTotal probability: {total_prob:.6f}")
    
    # Show some example paths
    print("\nExample Paths:")
    collision_paths = [p for p in paths if 'collision' in p['type']][:3]
    no_collision_paths = [p for p in paths if 'no_collision' in p['type']][:2]
    
    for i, path in enumerate(collision_paths + no_collision_paths):
        print(f"\nPath {i+1} ({path['type']}):")
        print(f"  Sequence: {path['sequence']}")
        print(f"  Conditions: {path['conditions'][:3]}...")  # Show first 3 conditions
        print(f"  Outcome: {path['outcome']}")
    
    return paths, probabilities

def extract_symbolic_paths():
    """Extract paths in the format similar to your original parser"""
    extractor = BirthdayPathExtractor(k=4, days=7)
    paths = extractor.extract_birthday_paths()
    
    symbolic_paths = []
    
    for path in paths:
        # Convert to format similar to your parseconditional output
        path_sequence = []
        
        # Add iteration conditions
        for i, condition in enumerate(path['conditions']):
            if 'b' in condition and '==' in condition:
                path_sequence.append((condition, 'True'))
            elif 'seen[' in condition:
                path_sequence.append((condition, 'True'))
        
        # Add outcome
        path_sequence.append(('Statements', [path['outcome']]))
        
        symbolic_paths.append(path_sequence)
    
    return symbolic_paths

if __name__ == "__main__":
    # Run the analysis
    paths, probabilities = analyze_birthday_paradox()
    
    print("\n" + "="*50)
    print("SYMBOLIC PATHS (parseconditional format):")
    print("="*50)
    
    # Show paths in your preferred format
    symbolic_paths = extract_symbolic_paths()
    
    # Show first 10 paths
    for i, path in enumerate(symbolic_paths[:10]):
        print(f"Path {i+1}: {path}")
    
    print(f"\n... and {len(symbolic_paths)-10} more paths")
    
    # Summary statistics
    collision_prob = sum(prob['probability'] for name, prob in probabilities.items() if 'collision' in name)
    print(f"\nSUMMARY:")
    print(f"Probability of collision: {collision_prob:.6f}")
    print(f"Probability of no collision: {probabilities.get('no_collision', {}).get('probability', 0):.6f}")
