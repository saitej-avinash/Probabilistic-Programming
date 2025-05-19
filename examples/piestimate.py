import random
import csv

def monte_carlo_pi_probability(num_points, csv_filename='points.csv'):
    inside_circle = 0
    all_points = []

    for _ in range(num_points):
        x = random.randint(0,315)
        y = random.randint(0,315)
        is_inside = x**2 + y**2 <= 315*315

        if is_inside:
            inside_circle += 1

        all_points.append([x, y, 'inside' if is_inside else 'outside'])

    # Save to CSV
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['x', 'y', 'position'])  # header
        writer.writerows(all_points)

    probability = inside_circle / num_points
    pi_estimate = 4 * probability
    return probability, pi_estimate

# Example run
points = 315*315
prob, pi_val = monte_carlo_pi_probability(points, 'monte_carlo_points.csv')

print(f"Estimated Probability (point in quarter circle): {prob}")
print(f"Estimated π: {pi_val}")
