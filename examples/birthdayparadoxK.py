import random

def has_collision_canonical(K=4, N=7):
    """
    Returns 1 if any two people share a birthday, else 0.
    Follows the same branching logic pattern as:
        if b1 == b0: return 1
        elif b2 == b0: return 1
        elif b2 == b1: return 1
        ...
        else: return 0
    """
    # sample birthdays
    birthdays = [random.randrange(N) for _ in range(K)]

    # manually unrolled 'if / elif / else' logic
    # check all earlier pairs in the same order
    for i in range(1, K):
        for j in range(i):
            if birthdays[i] == birthdays[j]:
                return 1
    return 0


# --- Run simulation ---
if __name__ == "__main__":
    K = 23    # number of people
    N = 365  # number of possible birthdays
    trials = 100000

    collisions = sum(has_collision_canonical(K, N) for _ in range(trials))
    prob = collisions / trials

    print(f"K={K}, N={N}")
    print(f"Estimated probability of shared birthday: {prob:.6f}")
