import random

def von_neumann_fair_coin(p=0.8):
    """
    Returns 0 or 1 with equal probability using a biased coin that
    returns 0 (H) with probability p and 1 (T) with probability (1-p).
    Uses only if and while constructs.
    """
    while True:
        # two biased flips
        if random.random() < p :
            a = 0
        else:
            a = 1

        if random.random() < p :
            b= 0 
        else :
            b =1

        # fair extraction logic
        if a == 0 and b == 1:
            return 0   # (H,T) → 0
        elif a == 1 and b == 0:
            return 1   # (T,H) → 1
        else : 
            return -1
        # else (HH or TT): repeat

# Example test
count0 = count1 = 0
for _ in range(100000):
    r = von_neumann_fair_coin(0.8)
    if r == 0:
        count0 += 1
    else:
        count1 += 1

print(f"P(0) = {count0/(count0+count1):.4f}, P(1) = {count1/(count0+count1):.4f}")
