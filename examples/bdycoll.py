import random

def birthday_paradox():
    N = 7  # number of possible birthdays

    # randomly assign birthdays
    b0 = random.randrange(N)
    b1 = random.randrange(N)
    b2 = random.randrange(N)
    b3 = random.randrange(N)
    if b1 == b0:
        return 1

    
    elif b2 == b0:
        return 1
    elif b2 == b1:
        return 1

    
    elif b3 == b0:
        return 1
    elif b3 == b1:
        return 1
    elif b3 == b2:
        return 1
    else:
        return 0

# Run simulation
trials = 1000000
collisions = sum(birthday_paradox() for _ in range(trials))
prob = collisions / trials

print(f"Estimated probability of shared birthday (K=4): {prob:.6f}")
