import random

def probabilistic_function():
    # x ~ UniformInt(1, 3)
    x = random.randint(1, 3)
    # y ~ UniformInt(1, 3)
    y = random.randint(1, 3)

    print("X and Y",x,y)
    
    # If-Else conditions
    if x > 1:
        if x < y:
            return True
        else:
            return False
    else:
        return False

# Run the function and print the result
result = probabilistic_function()
print("Result:", result)
