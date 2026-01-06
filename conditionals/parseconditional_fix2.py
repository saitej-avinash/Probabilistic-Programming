import ast

class ConditionNode:
    """A class representing a node in the condition tree."""
    def __init__(self, condition=None):
        self.condition = condition
        self.true_statements = []  # Store statements inside the True branch
        self.false_statements = []  # Store statements inside the False branch
        self.true_branch = None
        self.false_branch = None
        self.next_condition = None  # For sequential conditions at the same level

    def __repr__(self):
        return (
            f"ConditionNode(condition={self.condition}, "
            f"true_statements={self.true_statements}, false_statements={self.false_statements}, "
            f"true_branch={self.true_branch}, false_branch={self.false_branch}, "
            f"next_condition={self.next_condition})"
        )


class ConditionTreeBuilder(ast.NodeVisitor):
    def __init__(self):
        self.root = None  # Root of the condition tree
        self.current = None  # Tracks the current node

    def visit_If(self, node):
        # Create a new condition node
        condition = ast.unparse(node.test)
        condition_node = ConditionNode(condition=condition)

        if not self.root:
            # Set the root if it's the first condition
            self.root = condition_node
            self.current = condition_node
        else:
            # Handle sequential conditions (next independent condition)
            if self.current is not None:
                if self.current.next_condition is None:
                    self.current.next_condition = condition_node
                else:
                    current = self.current.next_condition
                    while current.next_condition:
                        current = current.next_condition
                    current.next_condition = condition_node

        # Update current pointer for nested conditions
        parent = self.current
        self.current = condition_node

        # Process the True branch
        true_branch_builder = ConditionTreeBuilder()
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                true_branch_builder.visit(stmt)
            else:
                # Store non-conditional statements in the True branch
                condition_node.true_statements.append(ast.unparse(stmt))
        condition_node.true_branch = true_branch_builder.root

        # Process the False branch
        false_branch_builder = ConditionTreeBuilder()
        if node.orelse:
            
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    false_branch_builder.visit(stmt)
                else:
                    # Store non-conditional statements in the False branch
                    condition_node.false_statements.append(ast.unparse(stmt))
        elif not self.current.next_condition :

            # **Implicit Else Handling**: If no else, add an empty false branch
            condition_node.false_statements.append("pass")  # Represents implicit execution

        condition_node.false_branch = false_branch_builder.root

        # Restore the current pointer to the parent
        self.current = parent

    def build_tree(self, code):
        # Parse the code into an AST and visit it
        tree = ast.parse(code)
        self.visit(tree)
        return self.root


def extract_paths(node, current_path=None, all_paths=None):
    """
    Recursively extract all paths from the condition tree.
    Each path represents a sequence of (condition, truth value) pairs leading to a leaf.
    Also includes statements inside each branch.
    """
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []

    if not node:
        return all_paths

    # True branch traversal
    if node.true_branch or node.true_statements:
        path = current_path + [(node.condition, "True")]
        if node.true_statements:
            path.append(("Statements", node.true_statements))
        if node.true_branch:
            extract_paths(node.true_branch, path, all_paths)
        else:
            all_paths.append(path)  # Ensure leaf paths are added

    # False branch traversal (handles missing branches)
    if node.false_branch or node.false_statements:
        path = current_path + [(node.condition, "False")]
        if node.false_statements:
            path.append(("Statements", node.false_statements))
        if node.false_branch:
            extract_paths(node.false_branch, path, all_paths)
        else:
            all_paths.append(path)  # Ensure leaf paths are added
        
        


    # Handle sequential (next_condition) **correctly** by keeping previous conditions
    if node.next_condition:
        extract_paths(node.next_condition, [], all_paths)  # Preserve `current_path`

    return all_paths



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
            else :
                choice =2 
        elif host_door == 2:
            if choice == 1 :
                choice = 3
            else: 
                choice= 1
        else:
            if choice == 1 :
                choice = 2
            else : 
                choice = 1

    
    if choice == car_door :
        return 1

"""

example_code7 = """
if 0*r_0 + 0*r_1 != 0:
    return False
elif 2*r_0 + 0*r_1 != 0:
    return False
else:
    return True    
if 0*r_0 + 0*r_1 != 0:
    return False
elif 2*r_0 + 0*r_1 != 0:
    return False
else:
    return True"""


example_code9 = """
 
def randminoftwo():
    x = ran.randint(1,10)
    y= ran.randint(1,10)

    if x<y :
        return 1
    else :
        return 0
"""
example_code8 = """

x = sample_uniform(1, 6)

if x > 3:
    y = 1
else:
    y = 0
"""

example_code6 = """
if x>1:
    if x>2:
        return 1
    else:
        return 0


if x>3:
    return 1
else : 
    return 2
"""


example_code10 = """

def freivalds():
    r0 = sample_uniform(0, 1)
    r1 = sample_uniform(0, 1)

    # Hardcoded incorrect matrices: A @ B ≠ C
    A = [[2, 3], [3, 4]]
    B = [[1, 0], [1, 2]]
    C = [[6, 5], [8, 8]]  # C is incorrect

    # Compute B @ r
    Br0 = 1 * r0 + 0 * r1
    Br1 = 1 * r0 + 2 * r1

    # A @ (B @ r)
    ABr0 = 2 * Br0 + 3 * Br1
    ABr1 = 3 * Br0 + 4 * Br1

    # C @ r
    Cr0 = 6 * r0 + 5 * r1
    Cr1 = 8 * r0 + 8 * r1

    # Check if Freivalds returns True
    if ABr0 == Cr0 and ABr1 == Cr1:
        return True
    else:
        return False


"""


example_montyhall = """

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
"""

example_montypi = """
if x**2 + y**2 <= 315*315:
    return 1
else:
    return 0
"""


example_bdy = """
def has_collision_canonical():
    if b1 == b0:
        return 1
    elif b2 == b0:
        return 1
    elif b2 == b1:
        return 1
    elif b3 == b0:
        return 1
    elif b3 == b1:
        return 1
    elif b3 == b2:
        return 1
    else : 
        return 0
"""

example_bdy12 = """
def birthday_paradox_chain(N=365):
    #b0 = random.randrange(N)
    #b1 = random.randrange(N)
    if b1 == b0:
        return 1
        #b2 = random.randrange(N)
    elif b2 == b0:
        return 1
    elif b2 == b1:
        return 1
        #b3 = random.randrange(N)
    elif b3 == b0:
        return 1
    elif b3 == b1:
        return 1
    elif b3 == b2:
        return 1
    else:
        return 0
"""
unrolled_bdy = """
def has_collision_canonical():
    if b1 == b0:
        return 1
    elif b2 == b0:
        return 1
    elif b2 == b1:
        return 1
    elif b3 == b0:
        return 1
    elif b3 == b1:
        return 1
    elif b3 == b2:
        return 1
    elif b4 == b0:
        return 1
    elif b4 == b1:
        return 1
    elif b4 == b2:
        return 1
    elif b4 == b3:
        return 1
    elif b5 == b0:
        return 1
    elif b5 == b1:
        return 1
    elif b5 == b2:
        return 1
    elif b5 == b3:
        return 1
    elif b5 == b4:
        return 1
    elif b6 == b0:
        return 1
    elif b6 == b1:
        return 1
    elif b6 == b2:
        return 1
    elif b6 == b3:
        return 1
    elif b6 == b4:
        return 1
    elif b6 == b5:
        return 1
    elif b7 == b0:
        return 1
    elif b7 == b1:
        return 1
    elif b7 == b2:
        return 1
    elif b7 == b3:
        return 1
    elif b7 == b4:
        return 1
    elif b7 == b5:
        return 1
    elif b7 == b6:
        return 1
    elif b8 == b0:
        return 1
    elif b8 == b1:
        return 1
    elif b8 == b2:
        return 1
    elif b8 == b3:
        return 1
    elif b8 == b4:
        return 1
    elif b8 == b5:
        return 1
    elif b8 == b6:
        return 1
    elif b8 == b7:
        return 1
    elif b9 == b0:
        return 1
    elif b9 == b1:
        return 1
    elif b9 == b2:
        return 1
    elif b9 == b3:
        return 1
    elif b9 == b4:
        return 1
    elif b9 == b5:
        return 1
    elif b9 == b6:
        return 1
    elif b9 == b7:
        return 1
    elif b9 == b8:
        return 1
    else:
        return 0
"""

unrolled_bdy23 = """
def has_collision_canonical():
    if b1 == b0:
        return 1
    elif b2 == b0:
        return 1
    elif b2 == b1:
        return 1
    elif b3 == b0:
        return 1
    elif b3 == b1:
        return 1
    elif b3 == b2:
        return 1
    elif b4 == b0:
        return 1
    elif b4 == b1:
        return 1
    elif b4 == b2:
        return 1
    elif b4 == b3:
        return 1
    elif b5 == b0:
        return 1
    elif b5 == b1:
        return 1
    elif b5 == b2:
        return 1
    elif b5 == b3:
        return 1
    elif b5 == b4:
        return 1
    elif b6 == b0:
        return 1
    elif b6 == b1:
        return 1
    elif b6 == b2:
        return 1
    elif b6 == b3:
        return 1
    elif b6 == b4:
        return 1
    elif b6 == b5:
        return 1
    elif b7 == b0:
        return 1
    elif b7 == b1:
        return 1
    elif b7 == b2:
        return 1
    elif b7 == b3:
        return 1
    elif b7 == b4:
        return 1
    elif b7 == b5:
        return 1
    elif b7 == b6:
        return 1
    elif b8 == b0:
        return 1
    elif b8 == b1:
        return 1
    elif b8 == b2:
        return 1
    elif b8 == b3:
        return 1
    elif b8 == b4:
        return 1
    elif b8 == b5:
        return 1
    elif b8 == b6:
        return 1
    elif b8 == b7:
        return 1
    elif b9 == b0:
        return 1
    elif b9 == b1:
        return 1
    elif b9 == b2:
        return 1
    elif b9 == b3:
        return 1
    elif b9 == b4:
        return 1
    elif b9 == b5:
        return 1
    elif b9 == b6:
        return 1
    elif b9 == b7:
        return 1
    elif b9 == b8:
        return 1
    elif b10 == b0:
        return 1
    elif b10 == b1:
        return 1
    elif b10 == b2:
        return 1
    elif b10 == b3:
        return 1
    elif b10 == b4:
        return 1
    elif b10 == b5:
        return 1
    elif b10 == b6:
        return 1
    elif b10 == b7:
        return 1
    elif b10 == b8:
        return 1
    elif b10 == b9:
        return 1
    elif b11 == b0:
        return 1
    elif b11 == b1:
        return 1
    elif b11 == b2:
        return 1
    elif b11 == b3:
        return 1
    elif b11 == b4:
        return 1
    elif b11 == b5:
        return 1
    elif b11 == b6:
        return 1
    elif b11 == b7:
        return 1
    elif b11 == b8:
        return 1
    elif b11 == b9:
        return 1
    elif b11 == b10:
        return 1
    elif b12 == b0:
        return 1
    elif b12 == b1:
        return 1
    elif b12 == b2:
        return 1
    elif b12 == b3:
        return 1
    elif b12 == b4:
        return 1
    elif b12 == b5:
        return 1
    elif b12 == b6:
        return 1
    elif b12 == b7:
        return 1
    elif b12 == b8:
        return 1
    elif b12 == b9:
        return 1
    elif b12 == b10:
        return 1
    elif b12 == b11:
        return 1
    elif b13 == b0:
        return 1
    elif b13 == b1:
        return 1
    elif b13 == b2:
        return 1
    elif b13 == b3:
        return 1
    elif b13 == b4:
        return 1
    elif b13 == b5:
        return 1
    elif b13 == b6:
        return 1
    elif b13 == b7:
        return 1
    elif b13 == b8:
        return 1
    elif b13 == b9:
        return 1
    elif b13 == b10:
        return 1
    elif b13 == b11:
        return 1
    elif b13 == b12:
        return 1
    elif b14 == b0:
        return 1
    elif b14 == b1:
        return 1
    elif b14 == b2:
        return 1
    elif b14 == b3:
        return 1
    elif b14 == b4:
        return 1
    elif b14 == b5:
        return 1
    elif b14 == b6:
        return 1
    elif b14 == b7:
        return 1
    elif b14 == b8:
        return 1
    elif b14 == b9:
        return 1
    elif b14 == b10:
        return 1
    elif b14 == b11:
        return 1
    elif b14 == b12:
        return 1
    elif b14 == b13:
        return 1
    elif b15 == b0:
        return 1
    elif b15 == b1:
        return 1
    elif b15 == b2:
        return 1
    elif b15 == b3:
        return 1
    elif b15 == b4:
        return 1
    elif b15 == b5:
        return 1
    elif b15 == b6:
        return 1
    elif b15 == b7:
        return 1
    elif b15 == b8:
        return 1
    elif b15 == b9:
        return 1
    elif b15 == b10:
        return 1
    elif b15 == b11:
        return 1
    elif b15 == b12:
        return 1
    elif b15 == b13:
        return 1
    elif b15 == b14:
        return 1
    elif b16 == b0:
        return 1
    elif b16 == b1:
        return 1
    elif b16 == b2:
        return 1
    elif b16 == b3:
        return 1
    elif b16 == b4:
        return 1
    elif b16 == b5:
        return 1
    elif b16 == b6:
        return 1
    elif b16 == b7:
        return 1
    elif b16 == b8:
        return 1
    elif b16 == b9:
        return 1
    elif b16 == b10:
        return 1
    elif b16 == b11:
        return 1
    elif b16 == b12:
        return 1
    elif b16 == b13:
        return 1
    elif b16 == b14:
        return 1
    elif b16 == b15:
        return 1
    elif b17 == b0:
        return 1
    elif b17 == b1:
        return 1
    elif b17 == b2:
        return 1
    elif b17 == b3:
        return 1
    elif b17 == b4:
        return 1
    elif b17 == b5:
        return 1
    elif b17 == b6:
        return 1
    elif b17 == b7:
        return 1
    elif b17 == b8:
        return 1
    elif b17 == b9:
        return 1
    elif b17 == b10:
        return 1
    elif b17 == b11:
        return 1
    elif b17 == b12:
        return 1
    elif b17 == b13:
        return 1
    elif b17 == b14:
        return 1
    elif b17 == b15:
        return 1
    elif b17 == b16:
        return 1
    elif b18 == b0:
        return 1
    elif b18 == b1:
        return 1
    elif b18 == b2:
        return 1
    elif b18 == b3:
        return 1
    elif b18 == b4:
        return 1
    elif b18 == b5:
        return 1
    elif b18 == b6:
        return 1
    elif b18 == b7:
        return 1
    elif b18 == b8:
        return 1
    elif b18 == b9:
        return 1
    elif b18 == b10:
        return 1
    elif b18 == b11:
        return 1
    elif b18 == b12:
        return 1
    elif b18 == b13:
        return 1
    elif b18 == b14:
        return 1
    elif b18 == b15:
        return 1
    elif b18 == b16:
        return 1
    elif b18 == b17:
        return 1
    elif b19 == b0:
        return 1
    elif b19 == b1:
        return 1
    elif b19 == b2:
        return 1
    elif b19 == b3:
        return 1
    elif b19 == b4:
        return 1
    elif b19 == b5:
        return 1
    elif b19 == b6:
        return 1
    elif b19 == b7:
        return 1
    elif b19 == b8:
        return 1
    elif b19 == b9:
        return 1
    elif b19 == b10:
        return 1
    elif b19 == b11:
        return 1
    elif b19 == b12:
        return 1
    elif b19 == b13:
        return 1
    elif b19 == b14:
        return 1
    elif b19 == b15:
        return 1
    elif b19 == b16:
        return 1
    elif b19 == b17:
        return 1
    elif b19 == b18:
        return 1
    elif b20 == b0:
        return 1
    elif b20 == b1:
        return 1
    elif b20 == b2:
        return 1
    elif b20 == b3:
        return 1
    elif b20 == b4:
        return 1
    elif b20 == b5:
        return 1
    elif b20 == b6:
        return 1
    elif b20 == b7:
        return 1
    elif b20 == b8:
        return 1
    elif b20 == b9:
        return 1
    elif b20 == b10:
        return 1
    elif b20 == b11:
        return 1
    elif b20 == b12:
        return 1
    elif b20 == b13:
        return 1
    elif b20 == b14:
        return 1
    elif b20 == b15:
        return 1
    elif b20 == b16:
        return 1
    elif b20 == b17:
        return 1
    elif b20 == b18:
        return 1
    elif b20 == b19:
        return 1
    elif b21 == b0:
        return 1
    elif b21 == b1:
        return 1
    elif b21 == b2:
        return 1
    elif b21 == b3:
        return 1
    elif b21 == b4:
        return 1
    elif b21 == b5:
        return 1
    elif b21 == b6:
        return 1
    elif b21 == b7:
        return 1
    elif b21 == b8:
        return 1
    elif b21 == b9:
        return 1
    elif b21 == b10:
        return 1
    elif b21 == b11:
        return 1
    elif b21 == b12:
        return 1
    elif b21 == b13:
        return 1
    elif b21 == b14:
        return 1
    elif b21 == b15:
        return 1
    elif b21 == b16:
        return 1
    elif b21 == b17:
        return 1
    elif b21 == b18:
        return 1
    elif b21 == b19:
        return 1
    elif b21 == b20:
        return 1
    elif b22 == b0:
        return 1
    elif b22 == b1:
        return 1
    elif b22 == b2:
        return 1
    elif b22 == b3:
        return 1
    elif b22 == b4:
        return 1
    elif b22 == b5:
        return 1
    elif b22 == b6:
        return 1
    elif b22 == b7:
        return 1
    elif b22 == b8:
        return 1
    elif b22 == b9:
        return 1
    elif b22 == b10:
        return 1
    elif b22 == b11:
        return 1
    elif b22 == b12:
        return 1
    elif b22 == b13:
        return 1
    elif b22 == b14:
        return 1
    elif b22 == b15:
        return 1
    elif b22 == b16:
        return 1
    elif b22 == b17:
        return 1
    elif b22 == b18:
        return 1
    elif b22 == b19:
        return 1
    elif b22 == b20:
        return 1
    elif b22 == b21:
        return 1
    else:
        return 0
        
"""
# Build the condition tree


randomsample = """
def check4(): 
    x =ran.randint(1,3)
    y= ran.randint(1,3)

    if  x>1 :
        if y>x:
            x=y
        else : 
            x = x+1
    if x>2:
        return 1
    return 0
"""

neumann = """
def von_neumann_fair_coin(p=0.8):

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

        
        if a == 0 and b == 1:
            return 0   # (H,T) → 0
        elif a == 1 and b == 0:
            return 1   # (T,H) → 1
        else :
            return -1
        
"""

Randmintwo = """
def randminoftwo():
    x = ran.randint(1,10)
    y= ran.randint(1,10)

    if x<y :
        return 1
    else :
        return 0

"""

Randmaxtwo = """
def randmaxoftwo():
    x = ran.randint(1, 10)
    y= ran.randint(1, 10)

    if x>y :
        return 1
    else :
        return 0

"""

Randeqltwo = """
def randeqloftwo():
    x = ran.randint(1, 10)
    y= ran.randint(1, 10)

    if x==y :
        return 1
    else :
        return 0

"""





builder = ConditionTreeBuilder()
#condition_tree = builder.build_tree(example_code9)

# Print the condition tree
#print("Condition Tree:")
#print(condition_tree)

# Extract all paths from the condition tree
#paths = extract_paths(condition_tree)

# Print the extracted paths
#print("\nExtracted Paths:")
#for path in paths:
  #  print(path)

#builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(example_code7)     
maxpaths = extract_paths(condition_tree)
print("\nExtracted Paths:")
for path in maxpaths:
    print(path)


"""
builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(Randeqltwo)     
eqlpaths = extract_paths(condition_tree)
print("\nExtracted Paths:")
for path in eqlpaths:
    print(path) 

builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(Randmintwo)     
minpaths = extract_paths(condition_tree)
print("\nExtracted Paths:")
for path in minpaths:
    print(path)
"""