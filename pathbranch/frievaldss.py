import random

N = 2
MOD = 2  # use arithmetic over a finite field; try 2 or a large prime

def freivald(a, b, c):
    # r in {0,1}^N
    r = [random.randrange(2) for _ in range(N)]

    # br = B*r (mod MOD)
    br = [sum((b[i][j] * r[j]) % MOD for j in range(N)) % MOD for i in range(N)]

    # cr = C*r (mod MOD)
    cr = [sum((c[i][j] * r[j]) % MOD for j in range(N)) % MOD for i in range(N)]

    # axbr = A*(B*r) (mod MOD)
    axbr = [sum((a[i][j] * br[j]) % MOD for j in range(N)) % MOD for i in range(N)]

    # accept if A*(B*r) == C*r (mod MOD)
    for i in range(N):
        if (axbr[i] - cr[i]) % MOD != 0:
            return False
    return True

def isProduct(a, b, c, k):
    for _ in range(k):
        if not freivald(a, b, c):
            return False
    return True

# Example (C is wrong on purpose)
a = [[1, 21], [3, 4]]
b = [[1, 11], [1, 1]]
c = [[1, 2], [1, 4]]  # incorrect product
k = 1
count = 0
x = 10000  # trials

for _ in range(x):
    if isProduct(a, b, c, k):
        count += 1

false_positive_rate = (count / x) * 100
print(f"False Positive Rate: {false_positive_rate:.2f}%")
