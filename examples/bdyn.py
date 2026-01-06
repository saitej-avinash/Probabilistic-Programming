import random

def birthday_paradox(K=4, N=365):
    """
    Returns 1 if any two people share a birthday, else 0.
    Follows the exact nested-if logic pattern you showed.
    """
    birthdays = []

    for i in range(K):
        # sample a new random birthday
        bi = random.randrange(N)

        # compare with all previous birthdays in order
        for j in range(i):
            if bi == birthdays[j]:
                return 1  # first duplicate found → early return
        birthdays.append(bi)

    # reached here only if all birthdays are distinct
    return 0


# --- Run a Monte Carlo simulation ---
if __name__ == "__main__":
    K = 4   # number of people
    N = 7  # number of possible birthdays
    trials = 100000

    collisions = sum(birthday_paradox(K, N) for _ in range(trials))
    prob = collisions / trials

    print(f"Estimated probability of shared birthday (K={K}): {prob:.6f}")
