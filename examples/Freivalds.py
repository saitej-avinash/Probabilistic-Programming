import random 
N = 2

# Function to check if ABx = Cx
def freivald(a, b, c) :
    # Generate a random vector
    r = [random.randrange(2) for _ in range(N)]

    # Compute B*r
    br = [sum(b[i][j] * r[j] for j in range(N)) for i in range(N)]

    # Compute C*r
    cr = [sum(c[i][j] * r[j] for j in range(N)) for i in range(N)]

    # Compute A*(B*r)
    axbr = [sum(a[i][j] * br[j] for j in range(N)) for i in range(N)]

    # Check if A*(B*r) - C*r == 0
    for i in range(N):
        if axbr[i] - cr[i] != 0:
            return False
    return True

# Runs k iterations of Freivald's Algorithm
def isProduct(a, b, c, k):
    for _ in range(k):
        if not freivald(a, b, c):
            return False
    return True

# Driver code
a = [[1, 2], [3, 4]]
b = [[1, 0], [0, 1]]
c = [[1, 2], [1, 4]]  # Incorrect product
k = 1
count = 0
x = 1000  # Number of trials

for _ in range(x):
    if isProduct(a, b, c, k):
        count += 1  # Count false positives
    

# Calculate false positive rate
false_positive_rate = (count / x) * 100
print(f"False Positive Rate: {false_positive_rate:.2f}%")
