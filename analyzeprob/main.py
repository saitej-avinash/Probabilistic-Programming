import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer import analyze_return_probabilities


from analyzer import analyze_return_probabilities

# Define your function as a string
example_code = """def monty_hall(choice, door_switch):
    
    
    car_door = random.randint(1, 3)
    host_door = None

    
    if choice == car_door:
        return not door_switch

    
    if choice != 1 and car_door != 1:
        host_door = 1
    elif choice != 2 and car_door != 2:
        host_door = 2
    else:
        host_door = 3

    
    if door_switch:
        if host_door == 1:
            if choice == 2:
                choice=3
                if choice == car_door : 
                    return 1
            else :
                choice =2 
                if choice == car_door : 
                    return 1
        elif host_door == 2:
            if choice == 1 :
                choice = 3
                if choice == car_door : 
                    return 1
            else: 
                choice= 1
                if choice == car_door : 
                    return 1
        else:
            if choice == 1 :
                choice = 2
                if choice == car_door : 
                    return 1
            else : 
                choice = 1
                if choice == car_door : 
                    return 1

   
 
"""

variables = ['choice', 'door_switch', 'car_door', 'host_door']
domain = {
    'choice': [1, 2, 3],
    'door_switch': [1,0],
    'car_door': [1, 2, 3],
    'host_door': [1, 2, 3]
}

result_distribution, path_probs = analyze_return_probabilities(example_code, variables, domain)

print("== Summary of Return Probabilities ==")
for ret_val, prob in result_distribution.items():
    print(f"Return {ret_val} → P = {prob:.4f}")
