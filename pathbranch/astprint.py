import ast

code = """
def monte_carlo_pi_probability(num_points):
    
    inside_circle = 0

    for _ in range(num_points):
        x = random.randint(0,315)
        y = random.randint(0,315)
        is_inside = x**2 + y**2 <= 315*315

        if is_inside:
            inside_circle += 1


    probability = inside_circle / num_points
    pi_estimate = 4 * probability
    return probability, pi_estimate
"""

# Parse code into an AST
tree = ast.parse(code)

# Pretty-print the AST
print(ast.dump(tree, indent=4))
