import random


def monte_carlo_pi_probability(num_points):

    inside_circle = 0

    for _ in range(num_points):
        x = random.randint(0,315)
        y = random.randint(0,315)
        
        if x**2 + y**2 <= 315*315 : 
            inside_circle += 1


    probability = inside_circle / num_points
    pi_estimate = 4 * probability
    return probability, pi_estimate

# Example run
points = 315*315
prob, pi_val = monte_carlo_pi_probability(points)

print(f"Estimated Probability (point in quarter circle): {prob}")
print(f"Estimated π: {pi_val}")
