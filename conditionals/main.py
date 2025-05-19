import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from condition_tree_builder import ConditionTreeBuilder
from path_extractor import extract_paths

example_code = """

def monty_hall(choice, door_switch):
    
    
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

builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(example_code)

paths = extract_paths(condition_tree)

print("\nExtracted Paths:")
for path in paths:
    print(path)
