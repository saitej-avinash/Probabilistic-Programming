import random

def simulate_fall_probability(prob_step_left, num_trials=1000, max_steps_per_trial=1000):
    """
    Simulates the probability that a drunkard falls off a cliff located at position -1.
    
    Parameters:
    - prob_step_left: Probability of stepping left (towards the cliff)
    - num_trials: Number of independent random walks to simulate
    - max_steps_per_trial: Maximum steps per trial before giving up
    
    Returns:
    - Estimated (simulated) probability of falling off the cliff
    """
    falls = 0
    for _ in range(num_trials):
        position = 0
        for _ in range(max_steps_per_trial):
            # Take a step: left with prob_step_left, right otherwise
             
            X = 0.1 * random.randint(0,9)

            if X < prob_step_left : 

                step = -1 
            else : 

                step = 1 
            position = position + step 

            if position == -1 : 
                
                falls +=1
                break # Stop simulation for this trial if fallen



    return falls / num_trials


def theoretical_fall_probability(prob_step_left):
    """
    Computes the theoretical probability of falling off a cliff based on biased random walk theory.
    
    When starting at position 0 and cliff is at -1:
    - If p < 0.5: fall probability = p / (1 - p)
    - If p >= 0.5: fall probability = 1 (almost surely falls)

    Derived from absorbing Markov chain for biased 1D random walk.
    """
    if prob_step_left >= 0.5:
        return 1.0
    else:
        return prob_step_left / (1 - prob_step_left)


# Simulate and compare for multiple values of left step probability
probabilities = [round(0.1 * i, 1) for i in range(1, 10)]  # p in [0.1, 0.9]

print(f"{'P(left)':>8} | {'Simulated':>12} | {'Theoretical':>12}")
print("-" * 38)

for p in probabilities:
    simulated = simulate_fall_probability(p)
    theoretical = theoretical_fall_probability(p)
    print(f"{p:>8.1f} | {simulated:>12.4f} | {theoretical:>12.4f}")
