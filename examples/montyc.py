import random

def monty_hall(choice):
    
    # Randomly select the door with the car
    car_door = random.randint(1, 3)
    host_door = None

    # If the player initially picks the car door and doesn't switch, they win
    #if choice == car_door:
       # return not door_switch

    # Determine the host's door to open (must be a goat door)
    if choice != 1 and car_door != 1:
        
            if choice == 2:
                
                if car_door == 3 : 
                    return 1
                
            else :
                 
                if car_door == 2 : 
                    return 1
    elif choice != 2 and car_door != 2:
        
            if choice == 1 :
                
                if car_door == 3 : 
                    return 1
            else: 
                
                if car_door == 1 : 
                    return 1
    elif choice != 3 and car_door !=3:
        
            if choice == 1 :
                
                if car_door == 2 : 
                    return 1
            else : 
                
                if car_door == 1 : 
                    return 1

    # If the player switches doors, change their choice
    
 
    # Check if the player's final choice matches the car door
    


# Example usage: Simulate the Monty Hall problem
num_trials = 10000
switch_wins = 0
stay_wins = 0

for _ in range(num_trials):
    # Randomly choose an initial door (1, 2, or 3)
    initial_choice = random.randint(1, 3)
    
    # Simulate staying
    # if monty_hall(initial_choice, door_switch=False):
    #     stay_wins += 1

    # Simulate switching
    if monty_hall(initial_choice):
        switch_wins += 1

print(f"Out of {num_trials} trials:")
print(f"Winning by staying: {num_trials - switch_wins} ({((num_trials - switch_wins )/ num_trials) * 100 :.2f}%)")
print(f"Winning by switching: {switch_wins} ({(switch_wins / num_trials) * 100:.2f}%)")
